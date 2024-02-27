<script lang="ts">
  import { useContexts, ContextType } from '$lib/context';
  import type { CitationResponse } from '../../../generated/client';

  export let citations: CitationResponse[];
  export let conversationId: string;

  const { apiClient, notificationStore } = useContexts([
    ContextType.API_CLIENT,
    ContextType.NOTIFICATION_STORE
  ]);

  const handleClickCitation = async (citation: CitationResponse) => {
    try {
      const blob = await apiClient.downloadCitationDocument(conversationId, citation.documentId);

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = citation.fileName;

      // Simulate a click event on the link
      link.click();

      // Clean up by revoking the object URL
      URL.revokeObjectURL(url);
    } catch (e: any) {
      notificationStore.handleError(e, `Failed to download the file - ${e.message}`);
    }
  };
</script>

{#each citations as citation}
  <div class="reference-container">
    <div class="reference-title">
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <span
        class="reference-filename"
        on:click={() => {
          handleClickCitation(citation);
        }}>{citation.fileName}&nbsp;</span
      >
      <span class="reference-title__page-number">pg. {citation.pageNumber}</span>
    </div>
    {citation.content}
  </div>
{/each}

<style lang="scss">
  @import '../../../global.scss';

  .reference-container {
    display: flex;
    flex-direction: column;
    padding: 4px 16px;
    border-radius: 15px;
    color: black;
    font-size: 12px;
  }

  .reference-filename:hover {
    cursor: pointer;
    text-decoration: underline;
  }

  .reference-title {
    font-weight: 600;
    color: $theme-blue;
    font-size: 14px;

    &__page-number {
      font-weight: 500;
      font-size: 14px;
      color: $theme-stale-grey;
    }
  }
</style>
