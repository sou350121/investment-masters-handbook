import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const PROJECT_ROOT = path.join(process.cwd(), '..');

export interface Investor {
  id: string;
  full_name: string;
  chinese_name: string;
  nationality?: string;
  // Representative company / fund (existing field in investor_index.yaml)
  fund?: string;
  intro_zh?: string;
  style: string[];
  best_for: string[];
  content?: string;
}

export interface Rule {
  rule_id: string;
  investor_id: string;
  kind: string;
  when: string;
  then: string;
  because?: string;
}

export async function getInvestors(): Promise<Investor[]> {
  const indexPath = path.join(PROJECT_ROOT, 'config', 'investor_index.yaml');
  const fileContents = fs.readFileSync(indexPath, 'utf8');
  const data = yaml.load(fileContents) as { investors: Investor[] };
  return data.investors;
}

export async function getInvestorById(id: string): Promise<Investor | null> {
  const investors = await getInvestors();
  const investor = investors.find(i => i.id === id);
  if (!investor) return null;

  const mdPath = path.join(PROJECT_ROOT, 'investors', `${id}.md`);
  if (fs.existsSync(mdPath)) {
    investor.content = fs.readFileSync(mdPath, 'utf8');
  }
  return investor;
}

export async function getRulesByInvestorId(id: string): Promise<Rule[]> {
  const rulesPath = path.join(PROJECT_ROOT, 'config', 'decision_rules.generated.json');
  if (!fs.existsSync(rulesPath)) return [];

  const fileContents = fs.readFileSync(rulesPath, 'utf8');
  const data = JSON.parse(fileContents);
  return (data.rules || []).filter((r: Rule) => r.investor_id === id);
}

export async function getProductManual(): Promise<string> {
  const manualPath = path.join(PROJECT_ROOT, 'PRODUCT_MANUAL.md');
  if (fs.existsSync(manualPath)) {
    return fs.readFileSync(manualPath, 'utf8');
  }
  return '';
}

export interface RagRequest {
  query: string;
  investor_id?: string;
  top_k?: number;
  source_type?: 'rule' | 'investor_doc';
  kind?: string;
}

export interface RagResponseItem {
  content: string;
  metadata: {
    investor_id: string;
    source: string;
    rule_id?: string;
    kind?: string;
    title_hint?: string;
  };
  similarity_estimate: number;
}
