import type { CompanyResponse } from '../../generated/client';

export type MessageRequestPayload = {
  message: string;
  upto?: string;
};

export type AttachmentUploadRequestPayload = {
  attachment: File;
  company: CompanyResponse;
  year: string;
};
