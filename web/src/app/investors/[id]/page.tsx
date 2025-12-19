import { getInvestorById, getRulesByInvestorId } from '@/lib/imh/data';
import InvestorDetail from '@/components/InvestorDetail';
import { notFound } from 'next/navigation';

export default async function InvestorPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params;
  const investor = await getInvestorById(id);
  
  if (!investor) {
    notFound();
  }

  const rules = await getRulesByInvestorId(id);

  return (
    <main>
      <InvestorDetail investor={investor} rules={rules} />
    </main>
  );
}
