<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';
  import {
    Table,
    TableBody,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
    Checkbox,
    Input,
    Select
  } from 'flowbite-svelte';
  import { CloseCircleSolid, ChevronRightOutline } from 'flowbite-svelte-icons';
  import { extractFileTableData, type FileTableData, type FileCompanyUpdate } from './types';

  export let onRequestClose: () => void;
  export let pendingUploadFiles: File[];
  export let onUploadFiles: (files: FileTableData[]) => void;
  export let showMaxFilesizeError = false;
  export let onSelectCompanyRequest: (filename: string) => void;
  export let fileUpdate: FileCompanyUpdate;

  const yearOptions = [
    { name: '2023', value: 2023 },
    { name: '2022', value: 2022 },
    { name: '2021', value: 2021 },
    { name: '2020', value: 2020 },
    { name: '2019', value: 2019 },
    { name: '2018', value: 2018 }
  ];

  let tableDataList: FileTableData[] = [];
  let numFilesChecked: number;
  let maxFilesAllowed = 20;
  let checkAll = true;
  let isUploadDisabled = true;

  $: {
    tableDataList = [
      ...tableDataList,
      ...pendingUploadFiles
        .filter(
          (pendingFile) =>
            !tableDataList.map((tableDataItem) => tableDataItem.filename).includes(pendingFile.name)
        )
        .map((pendingFile) => extractFileTableData(pendingFile))
    ];
  }
  $: {
    numFilesChecked = tableDataList.filter((tableData) => tableData.checked).length;
    if (tableDataList.every((tableData) => tableData.checked)) {
      checkAll = true;
    } else {
      checkAll = false;
    }
  }

  const handleUploadFiles = () => {
    onUploadFiles(tableDataList.filter((tableData) => tableData.checked));
    pendingUploadFiles = [];
    tableDataList = tableDataList.filter((tableData) => !tableData.checked);
    onRequestClose();
  };

  const handleParentCheckboxChange = (event: Event) => {
    tableDataList = tableDataList.map((tableData) => {
      tableData.checked = (event.target as HTMLInputElement).checked;
      return tableData;
    });
  };

  $: if (fileUpdate && tableDataList) {
    const selectedFileIndex = tableDataList.findIndex((it) => it.filename === fileUpdate.filename);
    if (selectedFileIndex !== -1)
      tableDataList[selectedFileIndex].company = fileUpdate.selectedCompany ?? null;
  }

  $: isUploadDisabled =
    numFilesChecked > maxFilesAllowed ||
    numFilesChecked === 0 ||
    tableDataList.some((it) => {
      if (it.checked) {
        return !it.company || !it.company.sub_sector_id || !it.year;
      } else return false;
    });

  function handleYearSelect(event: Event, file: FileTableData): void {
    const selectedFileIndex = tableDataList.findIndex((it) => it.filename === file.filename);
    if (selectedFileIndex !== -1)
      tableDataList[selectedFileIndex].year = Number((event.target as HTMLInputElement).value);
  }
</script>

<div>
  <div class="title-container">
    <div class="title">Pending Upload Files</div>
    <button
      class="focus:outline-none whitespace-normal p-2 m-0.5 rounded-lg focus:ring-2 p-1.5 focus:ring-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 ml-auto mb-4 dark:text-white"
      on:click={onRequestClose}
    >
      <img src={getImgPath(ImgType.IconModalClose)} alt="Close" width={14} />
    </button>
  </div>
  <div class="table-container">
    <Table hoverable={true}>
      <TableHead>
        <TableHeadCell class="!p-4">
          <Checkbox checked={checkAll} on:change={handleParentCheckboxChange} />
        </TableHeadCell>
        <TableHeadCell>File Name</TableHeadCell>
        <TableHeadCell>Company</TableHeadCell>
        <TableHeadCell>Year</TableHeadCell>
        <TableHeadCell>File Size</TableHeadCell>
      </TableHead>
      <TableBody tableBodyClass="divide-y">
        {#each tableDataList as tableData}
          <TableBodyRow>
            <TableBodyCell class="!p-4">
              <Checkbox
                checked={tableData.checked}
                on:change={() => {
                  tableData.checked = !tableData.checked;
                }}
              />
            </TableBodyCell>
            <TableBodyCell class="min-w-[220px] max-w-[350px] truncate"
              >{tableData.filename}</TableBodyCell
            >
            <TableBodyCell class="min-w-[250px] max-w-[500px]">
              <Input
                placeholder="Select Company"
                class="cursor-pointer"
                readOnly={true}
                value={tableData.company?.name}
                on:click={() => {
                  onSelectCompanyRequest(tableData.filename);
                }}
                ><ChevronRightOutline
                  slot="right"
                  strokeWidth="1.5"
                  class="text-[#aeb8c2] focus:outline-none hover:cursor-pointer hover:text-[#5c57f2]"
                  on:click={() => {
                    onSelectCompanyRequest(tableData.filename);
                  }}
                /></Input
              >
            </TableBodyCell>
            <TableBodyCell class="min-w-[175px]">
              <Select
                class="p-2"
                placeholder="Select Year"
                items={yearOptions}
                on:change={(event) => handleYearSelect(event, tableData)}
              /></TableBodyCell
            >

            <TableBodyCell>{tableData.fileSize}</TableBodyCell>
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  </div>
  {#if showMaxFilesizeError}
    <div class="text-sm text-red-500 file-size-error-msg">
      <CloseCircleSolid class="w-5 h-5 -ml-2 mr-1" />
      <span class="font-bold">Files greater than 10MB cannot be uploaded</span>
    </div>
  {/if}
  <div class="checked-files-msg-wrapper">
    {#if numFilesChecked <= maxFilesAllowed}
      <div class="text-sm text-gray-500">
        <span class="font-bold">{numFilesChecked}</span> of
        <span class="font-bold">{maxFilesAllowed}</span> files selected
      </div>
    {:else}
      <div class="text-sm text-red-500">
        <span class="font-bold">Maximum files allowed: {maxFilesAllowed}</span>
      </div>
    {/if}
  </div>
  <div class="actions">
    <button class="cancel-button" on:click={onRequestClose}>Cancel</button>
    <button class="upload-button" on:click={handleUploadFiles} disabled={isUploadDisabled}
      >Upload</button
    >
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .title-container {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    color: $theme-charcoal;
  }

  .table-container {
    max-height: calc(100vh - 16rem);
    overflow-y: auto;
    overflow-x: auto;
    @include custom-scroll-bar();
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

  .checked-files-msg-wrapper {
    margin-top: 8px;
  }

  .file-size-error-msg {
    display: flex;
    margin-top: 8px;
  }

  .add-company-button,
  .upload-button {
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
      background-color: $theme-stale-grey;
      cursor: not-allowed;
      -webkit-user-select: none; /* Safari */
      -ms-user-select: none; /* IE 10 and IE 11 */
      user-select: none; /* Standard syntax */
    }
  }
  .add-company-btn-container {
    padding-top: 10px;
    padding-bottom: 10px;
    text-align: center;
  }
  .add-company-button {
    padding: 10px;
  }

  :global(option) {
    color: $theme-charcoal;
    font-weight: 500;
  }
</style>
