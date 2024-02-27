import type {
  SubSectorService,
  SubsectorListResponse,
  SubsectorRequest
} from '../../generated/client';
import { makeRequest } from './request';

export function makeSubSectorAPIClient(subSectorService: SubSectorService) {
  async function addSubSector(newSubSector: SubsectorRequest) {
    return subSectorService.createSubsectorApiSubSectorPost(newSubSector);
  }

  async function listAllSubSectors() {
    return subSectorService.getSubsectorsApiSubSectorListGet();
  }

  //TODO: Use this API for pre fetch
  async function serverGetSubSectorsAndCompanies(
    serverFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>
  ) {
    return makeRequest<SubsectorListResponse>(
      `/api/sub-sector/list`,
      {
        method: 'GET'
      },
      serverFetch
    );
  }

  return {
    addSubSector,
    listAllSubSectors,
    serverGetSubSectorsAndCompanies
  };
}

export type SubSectorAPIClient = ReturnType<typeof makeSubSectorAPIClient>;
