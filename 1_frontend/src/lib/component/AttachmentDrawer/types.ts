import type { CompanyResponse } from '../../../generated/client';

export enum AttachmentIndexingStatus {
  Pending = 'Pending',
  Processing = 'Processing',
  Processed = 'Processed',
  Failure = 'Failure'
}

export type RemoteFile = {
  file: File;
  status: AttachmentIndexingStatus;
};

export type FileTableData = {
  checked: boolean;
  filename: string;
  fileSize: string;
  file: File;
  company: CompanyResponse | null;
  year: number | null;
};

export type FileCompanyUpdate = {
  filename: string;
  selectedCompany: CompanyResponse | null;
};

export function extractFileTableData(file: File): FileTableData {
  let fileSize: string;
  if (file.size < 1024) {
    fileSize = `${file.size} b`;
  } else if (file.size < 1024 * 1024) {
    fileSize = `${(file.size / 1024).toFixed(2)} kb`;
  } else {
    fileSize = `${(file.size / (1024 * 1024)).toFixed(2)} mb`;
  }
  return {
    checked: true,
    filename: file.name,
    fileSize,
    file,
    company: null,
    year: null
  };
}
