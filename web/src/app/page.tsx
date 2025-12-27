import { getInvestors, getProductManual } from '@/lib/imh/data';
import InvestorList from '@/components/InvestorList';
import { Box, Container } from '@mui/material';

export default async function Home() {
  const [investors, productManual] = await Promise.all([
    getInvestors(),
    getProductManual(),
  ]);

  return (
    <main>
      <Container maxWidth="lg">
        <InvestorList investors={investors} productManual={productManual} />
      </Container>
    </main>
  );
}
