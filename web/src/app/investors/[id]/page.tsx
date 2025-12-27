import { getInvestorById, getInvestors, getRulesByInvestorId } from '@/lib/imh/data';
import InvestorDetail from '@/components/InvestorDetail';
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
  const investors = await getInvestors();
  return investors.map((i) => ({ id: i.id }));
}

export default async function InvestorPage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const { id } = params;
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
