<script lang="ts">
  import { Label, Input, Tooltip } from 'flowbite-svelte';
  import classNames from 'classnames';
  import { ImgType, getImgPath } from '$lib/util/images';
  import { slide } from 'svelte/transition';
  import type { SubSectorCompanyState } from '../../../stores/subSectorCompanyStore';
  import { useContexts, ContextType } from '$lib/context';
  import { onDestroy } from 'svelte';
  import type { FileCompanyUpdate } from '../AttachmentDrawer/types';
  import { CloseCircleSolid, InfoCircleSolid } from 'flowbite-svelte-icons';
  import type { CompanyResponse, SubsectorResponse } from '../../../generated/client';

  export let onClose: () => void;
  export let onCompanySelect: (companySelection: FileCompanyUpdate) => void;
  export let filename: string;

  let subSectorCompanyState: SubSectorCompanyState;

  let selectedSubSector: SubsectorResponse;
  let selectedCompany: CompanyResponse | null;
  let subsectors: SubsectorResponse[];
  let companies: CompanyResponse[] | null;

  let newCompany: CompanyResponse;
  let newSubSector: SubsectorResponse;
  let newCompanyName: string;
  let newSubSectorName: string;

  let isSelectDisabled = true;
  let showAddCompanyField = false;
  let showAddSubSectorField = false;
  let showAddCompanyErrorMsg = false;
  let showAddSubSectorErrorMsg = false;

  const { apiClient, subSectorCompanyStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.SUBSECTOR_COMPANY_STORE
  ]);

  const unsubscribe = subSectorCompanyStore.subscribe((value) => {
    subSectorCompanyState = value;
  });

  $: subsectors = Array.from(subSectorCompanyState.subSectorCompanyMap.keys());

  $: if (!selectedSubSector) selectedSubSector = subsectors[0]; //default

  $: companies = subSectorCompanyState.subSectorCompanyMap.get(selectedSubSector) ?? null;

  $: isSelectDisabled = selectedCompany == null;

  const handleChangeCompanySelection = (company: CompanyResponse) => {
    selectedCompany = company;
  };
  const handleChangeSubSectorSelection = (subsector: SubsectorResponse) => {
    selectedSubSector = subsector;
    selectedCompany = null;
  };

  const setDefaultValues = () => {
    showAddCompanyErrorMsg = false;
    showAddSubSectorErrorMsg = false;
    showAddCompanyField = false;
    showAddSubSectorField = false;
    selectedCompany = null;
    selectedSubSector = subsectors[0];
  };

  const handleCompanySelection = () => {
    onCompanySelect({
      filename: filename,
      selectedCompany: selectedCompany
    });
    setDefaultValues();
    onClose();
  };

  function toggleShowAddCompanyField() {
    showAddCompanyField = !showAddCompanyField;
  }

  function toggleShowAddSubSectorField() {
    showAddSubSectorField = !showAddSubSectorField;
  }

  async function handleAddNewCompany() {
    try {
      //Handle Temporary ID for UI
      const tempId = `pending-company-${Date.now().toString()}`;
      newCompany = {
        id: tempId,
        name: newCompanyName,
        sub_sector_id: selectedSubSector.id
      };
      subSectorCompanyStore.addNewCompany(selectedSubSector, newCompany);
      selectedCompany = newCompany;

      //API Call
      const dbCompany = await apiClient.addCompany({
        name: newCompanyName,
        sub_sector_id: selectedSubSector.id
      });

      //Update local store
      subSectorCompanyStore.updateCompany(selectedSubSector, newCompany, dbCompany);
      selectedCompany = dbCompany;

      //Close error message and add company field
      showAddCompanyErrorMsg = false;
      toggleShowAddCompanyField();
      newCompanyName = '';
    } catch (e: any) {
      showAddCompanyErrorMsg = true;
      subSectorCompanyStore.removeCompany(selectedSubSector, newCompany);
    }
  }

  async function handleAddNewSubSector() {
    try {
      //Handle Temporary ID
      const tempId = `pending-subsector-${Date.now().toString()}`;
      newSubSector = {
        id: tempId,
        name: newSubSectorName,
        companies: []
      };
      subSectorCompanyStore.addNewSubSector(newSubSector);
      selectedSubSector = newSubSector;

      //API Call
      const dbSubSector = await apiClient.addSubSector({ name: newSubSectorName });

      //Update local store
      subSectorCompanyStore.updateSubSector(newSubSector, dbSubSector);
      selectedSubSector = dbSubSector;

      //Hide the text field and error message if previously displayed
      showAddSubSectorErrorMsg = false;
      toggleShowAddSubSectorField();
      newSubSectorName = '';
      selectedCompany = null;
    } catch (e: any) {
      showAddSubSectorErrorMsg = true;
      subSectorCompanyStore.removeSubSector(newSubSector);
    }
  }

  onDestroy(() => {
    unsubscribe();
  });
</script>

<div>
  <div class="header-container">
    <div class="title">Select Sub-sector & Company</div>
    <button
      class="focus:outline-none whitespace-normal p-2 rounded-lg focus:ring-2 p-1.5 focus:ring-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 dark:text-white"
      on:click={onClose}
    >
      <img src={getImgPath(ImgType.IconModalClose)} alt="Close" width={12} />
    </button>
  </div>
  <div class="file-name">File: {filename}</div>
  <div class="list-containers">
    <div class="subsectors-wrapper">
      <div class="label-wrapper">
        <Label class="font-semibold text-[#2a4359]">Select Sub-sector</Label>
        <button class="new-btn" on:click={toggleShowAddSubSectorField}>+ New</button>
      </div>
      {#if showAddSubSectorField}
        <div class="add-info" transition:slide={{ duration: 250 }}>
          <Input
            autofocus
            class="p-1 rounded"
            placeholder="Enter Sub-sector"
            bind:value={newSubSectorName}
            on:keydown={(event) => {
              if (showAddSubSectorErrorMsg) showAddSubSectorErrorMsg = false;
              if (
                event.key === 'Enter' &&
                newSubSectorName != null &&
                newSubSectorName.trim() !== ''
              )
                handleAddNewSubSector();
            }}
          >
            <div slot="right">
              <InfoCircleSolid strokeWidth="1.5" size="xs" />
              <Tooltip placement="right" class="text-xs"
                >Competitor questions will not be answered if a new sub-sector is added</Tooltip
              >
            </div></Input
          >

          <button
            class="add-btn"
            on:click={handleAddNewSubSector}
            disabled={newSubSectorName == null || newSubSectorName.trim() === ''}>Add</button
          >
        </div>
        {#if showAddSubSectorErrorMsg}
          <div class="error-msg">
            <CloseCircleSolid size="sm" class="mr-1" />
            <span>Failed to add sub-sector</span>
          </div>
        {/if}
      {/if}
      <div id="subsector-list" class="subsector-list">
        {#if subsectors && subsectors.length > 0}
          {#each subsectors as subsector}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
              class={classNames(
                'item',
                'truncate',
                subsector.id === selectedSubSector.id ? 'selected' : ''
              )}
              on:click={() => {
                handleChangeSubSectorSelection(subsector);
              }}
            >
              {subsector.name}
            </div>
          {/each}
        {:else if !showAddSubSectorField}
          <div class="no-item-message">No subsectors found</div>
        {/if}
      </div>
    </div>
    <div class="companies-wrapper">
      <div class="label-wrapper">
        <Label class="font-semibold text-[#2a4359]">Select Company</Label>
        <button class="new-btn" on:click={toggleShowAddCompanyField}>+ New</button>
      </div>
      {#if showAddCompanyField}
        <div class="add-info" transition:slide={{ duration: 250 }}>
          <Input
            autofocus
            class="p-1 rounded"
            placeholder="Enter Company name"
            bind:value={newCompanyName}
            on:keydown={(event) => {
              if (showAddCompanyErrorMsg) showAddCompanyErrorMsg = false;
              if (event.key === 'Enter' && newCompanyName != null && newCompanyName.trim() !== '')
                handleAddNewCompany();
            }}
          />
          <button
            class="add-btn"
            on:click={handleAddNewCompany}
            disabled={newCompanyName == null || newCompanyName.trim() === ''}>Add</button
          >
        </div>
        {#if showAddCompanyErrorMsg}
          <div class="error-msg">
            <CloseCircleSolid size="sm" class="mr-1" />
            <span>Failed to add company</span>
          </div>
        {/if}
      {/if}
      <div id="company-list" class="company-list">
        {#if companies && companies.length > 0}
          {#each companies as company}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
              class={classNames(
                'item',
                'truncate',
                company.id === selectedCompany?.id ? 'selected' : ''
              )}
              on:click={() => {
                handleChangeCompanySelection(company);
              }}
              on:dblclick={() => {
                handleChangeCompanySelection(company);
                handleCompanySelection();
              }}
            >
              {company.name}
            </div>
          {/each}
        {:else if !showAddCompanyField}
          <div class="no-item-message">No companies found</div>
        {/if}
      </div>
    </div>
  </div>
  <div class="select-btn-wrapper">
    <button class="select-company-btn" disabled={isSelectDisabled} on:click={handleCompanySelection}
      >Select Company</button
    >
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .header-container {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .file-name {
    margin-bottom: 24px;
    font-size: 12px;
    font-weight: 500;
    color: $theme-stale-grey;
    white-space: nowrap;
    overflow-x: hidden;
    text-overflow: ellipsis;
    max-width: 95%;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .search {
    position: sticky;
    top: 0px;
    background-color: white;
  }

  .label-wrapper {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    font-weight: 600;
    padding-bottom: 8px;
    border-bottom: 2px solid $theme-light-grey;
    margin-bottom: 8px;
  }

  .add-info {
    background-color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 8px;
    gap: 8px;
  }

  .new-btn {
    background-color: white;
    color: $theme-blue;
  }

  .new-btn:hover {
    color: darken($color: $theme-blue, $amount: 20%);
  }

  .add-btn,
  .select-company-btn {
    background-color: $theme-blue;
    color: white;
    border-radius: 4px;

    &:hover:not(:disabled) {
      background-color: darken($theme-blue, 10%);
      cursor: pointer;
    }

    &:disabled {
      background-color: $theme-stale-light-grey;
      cursor: not-allowed;
      -webkit-user-select: none; /* Safari */
      -ms-user-select: none; /* IE 10 and IE 11 */
      user-select: none; /* Standard syntax */
    }
  }

  .add-btn {
    font-size: 12px;
    padding: 5px 10px;
  }
  .select-btn-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: auto;
    padding-top: 12px;
    border-top: 2px solid $theme-light-grey;
  }
  .select-company-btn {
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 16px;
  }

  .subsectors-wrapper,
  .companies-wrapper {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 16rem; //TODO: fix the label width
    height: calc(100vh - 205px);

    @media (max-width: 540px) {
      max-height: calc(50vh - 115px);
    }
  }

  .no-item-message {
    font-size: 12px;
    color: $theme-stale-grey;
    cursor: default;
  }

  .subsector-list,
  .company-list {
    display: inline-block;
    overflow-y: auto;
    overflow-x: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow-y: auto;
    @include custom-scroll-bar();
    width: 100%;
    margin-bottom: 8px;
    padding-right: 8px;
  }

  .list-containers {
    display: flex;
    gap: 24px;

    @media (max-width: 540px) {
      flex-direction: column;
    }
  }

  .item {
    padding: 5px;
    border-radius: 4px;
    cursor: pointer;

    &:hover:not(.selected) {
      background-color: $theme-light-grey;
      color: black;
    }

    &.selected {
      background-color: $theme-blue;
      color: white;
    }
  }

  .error-msg {
    color: red;
    font-size: 12px;
    display: flex;
    font-weight: 600;
    align-items: center;
    padding-bottom: 8px;
  }
</style>
