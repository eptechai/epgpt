<script lang="ts">
  import type { TextRequestMessageItem } from '$lib/types';

  export let item: TextRequestMessageItem;
  export let userInitial = 'U';
</script>

<div class="message-item">
  <div class="message-wrapper">
    <div class="message">{item.data}</div>
    <div class="icon-wrapper">
      <div class="icon">{userInitial}</div>
    </div>
  </div>
</div>

<style lang="scss">
  @import '../../../global.scss';

  .message-item {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin: 8px;
    padding: 8px;
    border-radius: 16px;
  }

  .message-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: 48px;
  }

  .message {
    flex: 1;
    padding: 12px 16px;
    border-radius: 16px;
    background-color: $theme-blue;
    color: white;
    flex-wrap: wrap;
    word-wrap: break-word;
    white-space: pre-line;
  }

  .icon-wrapper {
    width: 40px;
    display: flex;
    flex-direction: column;
    align-self: flex-start;
  }

  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: white;
    color: $theme-blue;
    font-weight: 600;
    border: 2px solid $theme-blue;
    text-transform: uppercase;
    font-size: 1.2rem;
  }
</style>
