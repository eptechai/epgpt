import type { CitationResponse } from '../../generated/client';

export type Response = {
  id: string;
  response: string;
  citations: CitationResponse[];
  isFeedbackPositive: boolean | null;
};
