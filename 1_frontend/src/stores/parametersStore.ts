import { writable, get } from 'svelte/store';
import type { ParamsResponse } from '../generated/client';
import {
  convertLocalParamsResponsetoParamsResponse,
  defaultSelectedParams,
  getDefaultParams,
  type LocalParamsResponse,
  type NumericParamsResponseKeyArray
} from '$lib/component/ConfigModalView/types';

export interface ParametersState {
  parametersMap: Map<string, ParamsResponse>;
  configurableParameterOptionsMap: Map<string, NumericParamsResponseKeyArray>;
}

const initialState: ParametersState = {
  parametersMap: new Map(),

  // TODO: store the map in the local browser storage
  configurableParameterOptionsMap: new Map()
};

const createParametersStore = () => {
  const store = writable<ParametersState>(initialState);
  const { subscribe, update } = store;

  const getParamsResponse = (conversationId: string) => {
    const state = get(store);
    return state.parametersMap.get(conversationId) ?? getDefaultParams();
  };

  const getConfigurableParameterOptions = (conversationId: string) => {
    const state = get(store);
    return state.configurableParameterOptionsMap.get(conversationId) ?? defaultSelectedParams;
  };

  const setLocalParameters = (conversationId: string, localParamsResponse: LocalParamsResponse) => {
    const paramsResponse = convertLocalParamsResponsetoParamsResponse(localParamsResponse);
    update((currentState) => {
      const updatedParametersMap = new Map(currentState.parametersMap);
      updatedParametersMap.set(conversationId, { ...paramsResponse });

      return {
        ...currentState,
        parametersMap: updatedParametersMap
      };
    });
  };

  const setRemoteParameters = (conversationId: string, paramsResponse: ParamsResponse) => {
    update((currentState) => {
      const updatedParametersMap = new Map(currentState.parametersMap);
      updatedParametersMap.set(conversationId, { ...paramsResponse });

      return {
        ...currentState,
        parametersMap: updatedParametersMap
      };
    });
  };

  const setConfigurableParameterOptions = (
    conversationId: string,
    configurableParameterOptions: NumericParamsResponseKeyArray
  ) => {
    update((currentState) => {
      const updatedConfigurableParameterOptionsMap = new Map(
        currentState.configurableParameterOptionsMap
      );
      updatedConfigurableParameterOptionsMap.set(conversationId, [...configurableParameterOptions]);

      return {
        ...currentState,
        configurableParameterOptionsMap: updatedConfigurableParameterOptionsMap
      };
    });
  };

  const resetNumericParametersByKeys = (
    conversationId: string,
    paramKeys: NumericParamsResponseKeyArray
  ) => {
    update((currentState) => {
      const updatedParametersMap = new Map(currentState.parametersMap);
      const currentParamsResponse = updatedParametersMap.get(conversationId) ?? getDefaultParams();
      const defaultParamResponse = getDefaultParams();

      paramKeys.forEach((paramKey) => {
        currentParamsResponse[paramKey] = defaultParamResponse[paramKey];
      });

      updatedParametersMap.set(conversationId, { ...currentParamsResponse });

      return {
        ...currentState,
        parametersMap: updatedParametersMap
      };
    });
  };

  const resetState = (conversationId: string) => {
    update((currentState) => {
      const updatedParametersMap = new Map(currentState.parametersMap);
      updatedParametersMap.set(conversationId, { ...getDefaultParams() });

      const updatedConfigurableParameterOptionsMap = new Map(
        currentState.configurableParameterOptionsMap
      );
      updatedConfigurableParameterOptionsMap.set(conversationId, [...defaultSelectedParams]);

      return {
        ...currentState,
        configurableParameterOptionsMap: updatedConfigurableParameterOptionsMap,
        parametersMap: updatedParametersMap
      };
    });
  };

  return {
    subscribe,
    getParamsResponse,
    getConfigurableParameterOptions,
    setLocalParameters,
    setRemoteParameters,
    setConfigurableParameterOptions,
    resetNumericParametersByKeys,
    resetState
  };
};

export const parametersStore = createParametersStore();
export type ParametersStore = ReturnType<typeof createParametersStore>;
