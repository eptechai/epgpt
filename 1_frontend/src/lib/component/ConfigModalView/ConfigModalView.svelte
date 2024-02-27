<script lang="ts">
  import { page } from '$app/stores';
  import { onDestroy } from 'svelte';
  import type { ParametersState } from '../../../stores/parametersStore';
  import { ContextType, useContexts } from '$lib/context';
  import { Input, Helper, MultiSelect, Tabs, TabItem } from 'flowbite-svelte';
  import { ImgType, getImgPath } from '$lib/util/images';
  import {
    convertLocalParamsResponsetoParamsResponse,
    convertParamsResponsetoLocalParamsResponse,
    allParamViewConfigs,
    type LocalParamsResponse,
    type ParamsResponseItem,
    allParamOptionItems,
    defaultSelectedParams,
    type ParamViewConfig,
    getDefaultParams,
    type NumericParamsResponseKeyArray,
    type NumericParamsResponseKey
  } from './types';
  import { CONVO_PENDING_CREATION_ID } from '$lib/constants';

  export let onClose: () => void;
  export let isModalView = true;

  const { apiClient, parametersStore, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.PARAMETERS_STORE,
    ContextType.NOTIFICATION_STORE
  ]);

  let parametersState: ParametersState;
  const unsubscribe = parametersStore.subscribe((value) => {
    parametersState = value;
  });

  let id = $page.params.id;
  let localParameters: LocalParamsResponse;
  let configurableParameterOptions: NumericParamsResponseKeyArray;
  $: {
    id = $page.params.id;
    localParameters = convertParamsResponsetoLocalParamsResponse(
      parametersState.parametersMap.get(id) ??
        parametersState.parametersMap.get(CONVO_PENDING_CREATION_ID) ??
        getDefaultParams()
    );
    configurableParameterOptions =
      parametersState.configurableParameterOptionsMap.get(id) ?? defaultSelectedParams;
  }

  let numConfigs: ParamViewConfig;
  let errorMessageMap: {
    [key in NumericParamsResponseKey]: string | undefined;
  };
  $: {
    numConfigs = configurableParameterOptions.reduce((acc, key) => {
      acc[key] = allParamViewConfigs[key];
      acc[key].value = localParameters[key];
      return acc;
    }, {} as ParamViewConfig);
  }
  $: {
    errorMessageMap = configurableParameterOptions.reduce(
      (acc, key) => {
        acc[key] = undefined;
        return acc;
      },
      {} as {
        [key in NumericParamsResponseKey]: string | undefined;
      }
    );
  }
  $: hasValidationError = Object.values(errorMessageMap).some((value) => value !== undefined);

  function handleNumInput(event: Event, field: NumericParamsResponseKey) {
    const input = event.target as HTMLInputElement;

    if (numConfigs[field].max < parseFloat(input.value)) {
      errorMessageMap[field] = `Value cannot be greater than ${numConfigs[field].max}`;
    } else if (numConfigs[field].min > parseFloat(input.value)) {
      errorMessageMap[field] = `Value cannot be less than ${numConfigs[field].min}`;
    } else {
      errorMessageMap[field] = undefined;
    }
    localParameters[field] = input.value;
  }

  const apply = async () => {
    try {
      if (id === undefined) {
        // Note: Update the local writable store
        parametersStore.setLocalParameters(CONVO_PENDING_CREATION_ID, localParameters);
        onClose();
        return;
      }
      // Note: Update the Conversation Params and Update the local writable store
      const paramsResp = await apiClient.updateConversationParams(
        id,
        convertLocalParamsResponsetoParamsResponse(localParameters)
      );
      parametersStore.setRemoteParameters(id, paramsResp);
      onClose();
    } catch (e: any) {
      notificationStore.handleError(
        e,
        `Failed to apply the changes to configuration - ${e.message}`
      );
    }
  };

  const cancel = () => {
    // Note: Revert the changes to the local writable store
    parametersStore.setLocalParameters(
      id,
      convertParamsResponsetoLocalParamsResponse(
        parametersState.parametersMap.get(id) ?? getDefaultParams()
      )
    );
    onClose();
  };

  const handleSelect = (event: CustomEvent) => {
    const { detail } = event;
    const newArr: string[] = event.detail;

    // Note: Reset the parameters if the user removes them from the configurable parameters
    if (newArr.length <= configurableParameterOptions.length) {
      const removedItems = configurableParameterOptions.filter((it) => !newArr.includes(it));
      parametersStore.resetNumericParametersByKeys(id, removedItems);
    }

    parametersStore.setConfigurableParameterOptions(
      id,
      (detail as ParamsResponseItem[]).map((it) => it.value)
    );
  };

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div class="container">
  <div class="title-container">
    <div class="title">LLM Configurations</div>
    <button
      class="focus:outline-none whitespace-normal p-2 m-0.5 rounded-lg focus:ring-2 p-1.5 focus:ring-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 ml-auto mb-4 dark:text-white"
      on:click={onClose}
    >
      <img src={getImgPath(ImgType.IconModalClose)} alt="Close" width={14} />
    </button>
  </div>
  <p class="mb-6 text-sm text-gray-500">
    The configurations are parameters for the LLM model. The default values are recommended for best
    model performance.
  </p>
  <Tabs contentClass="bg-white p-2 mt-4" style="underline">
    <TabItem open title="General">
      <div class="common-fields">
        {#each Object.values(numConfigs) as { label, fieldName, placeholder, type, value }}
          <div class="field">
            <div class="label">{label}</div>
            <Input
              id={`input-${fieldName}`}
              defaultClass="block w-full border-0 border-b-2 border-b-transparent focus:border-b-2 focus:border-solid"
              {type}
              {placeholder}
              {value}
              color={errorMessageMap[fieldName] ? 'red' : 'base'}
              on:input={(e) => handleNumInput(e, fieldName)}
            />
            {#if !!errorMessageMap[fieldName]}
              <Helper class="flex self-start mt-2" color="red">{errorMessageMap[fieldName]}</Helper>
            {/if}
          </div>
        {/each}
      </div>
    </TabItem>
    <TabItem title="Advanced">
      <MultiSelect
        items={allParamOptionItems}
        bind:value={configurableParameterOptions}
        on:selected={handleSelect}
        dropdownClass="dropdown-class"
      />
    </TabItem>
  </Tabs>
  {#if isModalView}
    <div class="actions">
      <button class="cancel-button" on:click={cancel}>Cancel</button>
      <button class="apply-button" disabled={hasValidationError} on:click={apply}>Apply</button>
    </div>
  {/if}
</div>

<style lang="scss">
  @import '../../../global.scss';

  .container {
    min-width: 200px;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 90px);
  }

  .title-container {
    display: flex;
    align-items: center;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .common-fields {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    padding: 0px 16px;
    margin: auto auto 0;

    max-height: calc(100vh - 250px);
    overflow-y: auto;

    @include custom-scroll-bar();
  }

  .field {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: calc(50% - 8px);
    box-sizing: border-box;
    border-radius: 20px;
    font-weight: 600;
    display: flex;
    align-items: center;

    @media (max-width: 540px) {
      min-width: 100%;
    }
  }

  .actions {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    width: 100%;
    margin-top: 32px;
    gap: 16px;
  }

  .cancel-button {
    padding: 10px 16px;
    font-size: 16px;
    border-radius: 4px;

    &:hover:not(:disabled) {
      background-color: darken(white, 5%);
      cursor: pointer;
    }
  }

  .apply-button {
    background-color: $theme-blue;
    color: white;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 16px;

    &:hover:not(:disabled) {
      background-color: darken($theme-blue, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: #999999;
      cursor: not-allowed;
    }
  }

  .label {
    font-weight: 600;
    color: $theme-charcoal;
    display: flex;
    align-self: flex-start;
    margin-bottom: 4px;
  }

  .field_input {
    font-weight: 600;
    background-color: $theme-stale-light-grey-2;
    color: $theme-charcoal;
    text-align: center;
    border-radius: 6px;
    outline: none; /* Remove the default outline */
    outline-offset: 0; /* Make sure no outline space is reserved */
    border: none;
  }

  .field_input:active,
  .field_input:focus {
    border-bottom: 2px solid $theme-skyblue;
  }

  .configure-banner {
    position: absolute;
    top: -14px;
    display: flex;
    align-items: center;
    align-self: center;
    background-color: $theme-skyblue;
    color: white;
    padding: 2px 18px;
    font-size: 14px;

    transition: background-color 0.3s ease-in-out;
    height: 30px;
    border-radius: 15px;

    box-shadow: 0 4px 6px $theme-stale-light-grey;
  }
  :global(.dropdown-class) {
    @include custom-scroll-bar();
  }

  .error {
    color: red;
  }
</style>
