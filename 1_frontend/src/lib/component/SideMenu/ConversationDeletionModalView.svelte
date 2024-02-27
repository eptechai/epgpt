<script lang="ts">
  import { ImgType, getImgPath } from '$lib/util/images';

  export let conversationId: string;
  export let onRequestClose: () => void;
  export let onDelete: (conversationId: string) => void;

  const handleConversationDelete = () => {
    onDelete(conversationId);
    onRequestClose();
  };
</script>

<div>
  <div class="title-container">
    <div class="title">Delete Conversation?</div>
    <button
      class="focus:outline-none whitespace-normal p-2 m-0.5 rounded-lg focus:ring-2 p-1.5 focus:ring-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 ml-auto mb-4 dark:text-white"
      on:click={onRequestClose}
    >
      <img src={getImgPath(ImgType.IconModalClose)} alt="Close" width={14} />
    </button>
  </div>
  <div class="content">
    <p class="content-text">
      Are you sure you want to delete <span class="content-highlight">{conversationId}</span>?
      <br />This action cannot be undone.
    </p>
  </div>
  <div class="actions">
    <button class="cancel-button" on:click={onRequestClose}>Cancel</button>
    <button class="delete-button" on:click={handleConversationDelete}>Delete</button>
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

  .content {
    padding: 16px;
  }

  .content-text {
    font-size: 16px;
    color: $theme-charcoal;
    line-height: 1.5;
  }

  .content-highlight {
    font-weight: 600;
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

  .delete-button {
    background-color: red;
    color: white;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 16px;

    &:hover:not(:disabled) {
      background-color: darken(red, 10%);
      cursor: pointer;
    }
  }
</style>
