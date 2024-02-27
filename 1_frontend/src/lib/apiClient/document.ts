import { makeFileRequest, type RequestData } from './request';

export function makeDocumentAPIClient() {
  const downloadCitationDocument = (conversationId: string, documentId: string) => {
    const requestData: RequestData = {
      method: 'GET'
    };
    return makeFileRequest(
      `/api/conversation/${conversationId}/documents/${documentId}/`,
      requestData
    );
  };

  return {
    downloadCitationDocument
  };
}

export type DocumentAPIClient = ReturnType<typeof makeDocumentAPIClient>;
