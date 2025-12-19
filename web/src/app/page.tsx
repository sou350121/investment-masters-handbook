import { getInvestors } from '@/lib/imh/data';
import InvestorList from '@/components/InvestorList';
import { Box, Container } from '@mui/material';

export default async function Home() {
  const investors = await getInvestors();

  return (
    <main>
      <Container maxWidth="lg">
        <InvestorList investors={investors} />
      </Container>
    </main>
  );
}
