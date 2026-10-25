export interface Session {
  token: string;
  role: string;
  trader_id: string;
  display_name: string;
  username: string;
}

export interface CustomerOption {
  customer_id: string;
  name: string;
}

export interface FrameworkChoice {
  id: string;
  label: string;
  connected: boolean;
}

export interface Evidence {
  source: string;
  record_id: string;
  detail: string;
}

export interface AgentFinding {
  agent: string;
  model: string;
  model_called: boolean;
  summary: string;
  evidence: Evidence[];
}

export interface Alternative {
  product_name: string;
  reason: string;
}

export interface Recommendation {
  product_id: string;
  product_name: string;
  amount: number;
  currency: string;
  rationale: string;
  evidence: Evidence[];
  alternatives: Alternative[];
  risks: string[];
  assumptions: string[];
  next_steps: string[];
  trader_decides: boolean;
}

export interface Assurance {
  passed: boolean;
  confirm_allowed: boolean;
  checks: { name: string; passed: boolean; detail: string }[];
}

export interface Turn {
  turn_id: string;
  customer_id: string;
  framework: string;
  connected: boolean;
  question: string;
  agents: AgentFinding[];
  recommendation: Recommendation | null;
  assurance: Assurance;
  message: string;
  confirm_allowed: boolean;
}

export interface TurnPage {
  page: number;
  page_size: number;
  total: number;
  turns: Turn[];
}
