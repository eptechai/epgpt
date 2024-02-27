import type { CompanyRequest, CompanyService } from '../../generated/client';

export function makeCompanyAPIClient(companyService: CompanyService) {
  async function addCompany(newCompany: CompanyRequest) {
    return companyService.createCompanyApiCompanyPost(newCompany);
  }

  return {
    addCompany
  };
}

export type CompanyAPIClient = ReturnType<typeof makeCompanyAPIClient>;
