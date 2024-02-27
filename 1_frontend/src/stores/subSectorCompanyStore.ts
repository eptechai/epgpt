import { writable } from 'svelte/store';
import type { CompanyResponse, SubsectorResponse } from '../generated/client';

export interface SubSectorCompanyState {
  subSectorCompanyMap: Map<SubsectorResponse, CompanyResponse[]>;
}

const initialState: SubSectorCompanyState = {
  subSectorCompanyMap: new Map()
};

const createSubSectorCompanyStore = () => {
  const { subscribe, update, set } = writable<SubSectorCompanyState>(initialState);

  const createNewSubSectorMap = (map: Map<SubsectorResponse, CompanyResponse[]>) => {
    set({ subSectorCompanyMap: map });
  };

  const addNewCompany = (subSector: SubsectorResponse, company: CompanyResponse) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;
      subSectorCompanyMap.get(subSector)?.push(company);

      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  const updateCompany = (
    subSector: SubsectorResponse,
    existingCompany: CompanyResponse,
    updatedCompany: CompanyResponse
  ) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;

      const companies = subSectorCompanyMap.get(subSector);
      if (companies) {
        const index = companies?.findIndex((it) => it.id === existingCompany.id);
        if (index !== -1) companies[index].id = updatedCompany.id;
      }

      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  const removeCompany = (subSector: SubsectorResponse, company: CompanyResponse) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;

      const companies = subSectorCompanyMap.get(subSector);

      if (companies)
        subSectorCompanyMap.set(
          subSector,
          companies.filter((it) => it.id !== company.id)
        );

      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  const addNewSubSector = (subSector: SubsectorResponse) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;
      subSectorCompanyMap.set(subSector, []);

      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  const updateSubSector = (
    existingSubSector: SubsectorResponse,
    updatedSubSector: SubsectorResponse
  ) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;
      const existingCompanies = subSectorCompanyMap.get(existingSubSector);
      subSectorCompanyMap.delete(existingSubSector);
      subSectorCompanyMap.set(updatedSubSector, existingCompanies ?? []);
      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  const removeSubSector = (subSector: SubsectorResponse) => {
    update((currentState) => {
      const subSectorCompanyMap = currentState.subSectorCompanyMap;
      subSectorCompanyMap.delete(subSector);
      return {
        subSectorCompanyMap: subSectorCompanyMap
      };
    });
  };

  return {
    subscribe,
    addNewCompany,
    createNewSubSectorMap,
    addNewSubSector,
    removeCompany,
    removeSubSector,
    updateCompany,
    updateSubSector
  };
};

export const subSectorCompanyStore = createSubSectorCompanyStore();
export type SubSectorCompanyStore = ReturnType<typeof createSubSectorCompanyStore>;
