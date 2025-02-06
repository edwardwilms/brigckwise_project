import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { 
  DollarSign, 
  Clock, 
  PieChart,
  BarChart,
  TrendingUp,
  Building,
  Calculator,
  Percent,
  Activity
} from 'lucide-react';

const inputFields = [
  { key: 'operacao_total', label: 'OPERAÇÃO TOTAL', tooltip: 'Valor total financiado', cell: 'C7' },
  { key: 'financiamento', label: 'FINANCIAMENTO', tooltip: 'Valor do financiamento do projeto', cell: 'D8' },
  { key: 'metragem_terreno', label: 'METRAGEM TERRENO', tooltip: 'Área total do terreno em m²', cell: 'C13' },
  { key: 'metragem_total_venda', label: 'METRAGEM TOTAL - VENDA', tooltip: 'Área total disponível para venda', cell: 'C14' },
  { key: 'metragem_equivalente_construcao', label: 'METRAGEM EQUIVALENTE DE CONSTRUÇÃO', tooltip: 'Área equivalente de construção', cell: 'C15' },
  { key: 'custo_m2_construcao', label: 'CUSTO/M² CONSTRUÇÃO', tooltip: 'Custo por metro quadrado de construção', cell: 'C16' },
  { key: 'preco_m2_venda', label: 'PREÇO/M² ESPERADO DE VENDA', tooltip: 'Preço esperado por metro quadrado para venda', cell: 'C17' },
  { key: 'preco_terreno', label: 'PREÇO TERRENO', tooltip: 'Valor total do terreno', cell: 'C19' },
  { key: 'custo_construcao', label: 'CUSTO CONSTRUÇÃO', tooltip: 'Custo total da construção', cell: 'D21' },
  { key: 'custo_construcao_prazo', label: 'CUSTO CONSTRUÇÃO PRAZO', tooltip: 'Prazo da construção', cell: 'E21' },
  { key: 'taxa_performance', label: 'TAXA DE PERFORMANCE (%)', tooltip: 'Taxa de performance do projeto', type: 'percentage', cell: 'D24' },
  { key: 'corretagem', label: 'CORRETAGEM (%)', tooltip: 'Taxa de corretagem', type: 'percentage', cell: 'C27' }
];

const outputFields = [
  {
    key: 'lucro_liquido',
    label: 'LUCRO LÍQUIDO',
    icon: DollarSign,
    color: 'text-green-500'
  },
  {
    key: 'roi',
    label: 'ROI',
    icon: TrendingUp,
    color: 'text-emerald-500'
  },
  {
    key: 'tir_mensal',
    label: 'TIR MENSAL',
    icon: Percent,
    color: 'text-cyan-500'
  },
  { 
    key: 'exposicao_caixa',
    label: 'EXPOSIÇÃO DE CAIXA',
    icon: DollarSign,
    color: 'text-red-500'
  },
  {
    key: 'meses_payback',
    label: 'MESES PAYBACK',
    icon: Clock,
    color: 'text-green-500'
  },
  {
    key: 'corretagem_venda',
    label: 'CORRETAGEM VENDA',
    icon: Building,
    color: 'text-purple-500'
  },
  {
    key: 'taxa_sucesso',
    label: 'TAXA DE SUCESSO',
    icon: Activity,
    color: 'text-yellow-500'
  },
  {
    key: 'lucro_bruto',
    label: 'LUCRO BRUTO',
    icon: BarChart,
    color: 'text-green-500'
  },
  {
    key: 'ir_ganho_capital',
    label: 'I.R. CAPITAL',
    icon: Calculator,
    color: 'text-orange-500'
  },
];

const Dashboard = () => {
  const [inputs, setInputs] = useState(
    Object.fromEntries(inputFields.map(field => [field.key, 0]))
  );
  const [outputs, setOutputs] = useState(
    Object.fromEntries(outputFields.map(field => [field.key, 0]))
  );
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchExcelData = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await fetch('http://localhost:8000/read-excel', {
          method: 'GET'
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        setInputs(data.inputData);
        setOutputs(data.outputData);
      } catch (err) {
        console.error("Error fetching Excel data:", err);
        setError(typeof err === 'object' ? JSON.stringify(err) : err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchExcelData();
  }, []);

  const handleInputChange = (key, value) => {
    console.log("Starting calculation...");
    setInputs(prev => ({
      ...prev,
      [key]: parseFloat(value) || 0
    }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError('');

    try {
      // 1. Gather input values
      const inputValues = Object.fromEntries(
        inputFields.map(({ key }) => [key, inputs[key]])
      );

      // Validate input values before calculation
      const isValid = Object.values(inputs).every(value => value > 0);
      if (!isValid) {
          setError("All input values must be greater than 0.");
          setLoading(false);
          return;
      }
      
      console.log("Input values for update-excel:", inputValues);

      // 2. Update Excel file
      const response = await fetch('http://localhost:8000/update-excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputValues)
      });
      const data = await response.json();
      console.log("Response from update-excel:", data);
      if (!response.ok) throw new Error(data.detail);

      // 3. Read input values from Excel
      const readExcelResponse = await fetch('http://localhost:8000/read-excel', {
        method: 'GET'
      });
      const readExcelData = await readExcelResponse.json();
      console.log("Response from read-excel:", readExcelData);
      if (!readExcelResponse.ok) throw new Error(readExcelData.detail);
      // setInputs(readExcelData.inputData);
      setOutputs(readExcelData.outputData);
    } catch (err) {
      console.error("Error during calculation:", err);
      setError(typeof err === 'object' ? JSON.stringify(err) : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex justify-between items-center">
            <h1 className="text-4xl font-bold text-gray-900">Investment Dashboard</h1>
            <Button onClick={handleCalculate}>
              {loading ? 'Calculating...' : 'Calculate'}
            </Button>
          </div>

          <Card>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6">
            {inputFields.map(({ key, label, tooltip, type }) => (
              <Tooltip key={key}>
                <TooltipTrigger asChild>
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">
                      {label}
                    </label>
                    <Input
                      type="text" // Change to text to allow formatted display
                      value={
                        inputs[key] != null
                          ? parseFloat(inputs[key]).toLocaleString('pt-BR', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })
                          : ''
                      }
                      onChange={(e) => {
                        // Remove formatting for the value stored in the state
                        const rawValue = e.target.value.replace(/\./g, '').replace(',', '.');
                        handleInputChange(key, rawValue);
                      }}
                      min={0}
                      max={type === 'percentage' ? 100 : undefined}
                      step={type === 'percentage' ? 0.01 : 0.01}
                    />
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{tooltip}</p>
                </TooltipContent>
              </Tooltip>
            ))}
          </CardContent>

          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {outputFields.map(({ key, label, icon: Icon, color }) => (
              <Card key={key} className={`bg-white shadow-md ${key === 'lucro_liquido' || key === 'roi' || key === 'tir_mensal' ? 'transform transition-all hover:scale-105 shadow-2xl' : ''}`}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-gray-50 ${color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{label}</p>
                      <p className="text-xl font-bold mt-1">
                        {key === 'lucro_liquido' ? 
                          outputs[key]?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) :
                          key === 'roi' || key === 'tir_mensal' ?
                          `${outputs[key].toFixed(2)}%` :
                          key === 'exposicao_caixa' || key === 'taxa_sucesso' || key === 'corretagem_venda' || key === 'lucro_bruto' || key === 'ir_ganho_capital' ?
                          outputs[key]?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) :
                          key === 'meses_payback' ?
                          Math.round(outputs[key]) :
                          outputs[key]?.toLocaleString('pt-BR', {
                            style: key.includes('percentage') ? 'percent' : 'decimal',
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                          }) || '0,00'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>


          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
};

export default Dashboard;