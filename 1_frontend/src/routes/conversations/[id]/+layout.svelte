<script lang="ts">
  import { ContextType, useContexts } from '$lib/context';

  export let data;

  const { conversationStore, attachmentListStore, parametersStore } = useContexts([
    ContextType.CONVERSATION_STORE,
    ContextType.ATTACHMENT_LIST_STORE,
    ContextType.PARAMETERS_STORE
  ]);

  $: if (data.remoteDialogueItems) {
    conversationStore.setDialogueItemList(data.conversationId, data.remoteDialogueItems);
  }
  $: if (data.attachmentItems) {
    attachmentListStore.setAttachmentItemList(data.conversationId, data.attachmentItems);
  }
  $: if (data.parametersResp) {
    parametersStore.setRemoteParameters(data.conversationId, data.parametersResp);
  }
</script>

<main>
  <slot />
</main>
