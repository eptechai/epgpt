<script lang="ts">
  import { MenuItemType, type MenuItem } from './types';
  import classNames from 'classnames';

  export let item: MenuItem;
  export let isSelected: boolean;
  export let onItemClicked: (item: MenuItem) => void;

  const onClicked = (): void => {
    onItemClicked(item);
  };
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  class={classNames('menu-item-container', isSelected ? 'menu-item-container--selected' : '')}
  on:click={onClicked}
>
  <i>IC</i>
  <div class="menu-item">
    {#if item.type === MenuItemType.Conversation}
      <div class={classNames('menu-item-title', isSelected ? 'menu-item-title--selected' : '')}>
        {item.conversation.id}
      </div>
    {/if}
    {#if item.type === MenuItemType.Badge}
      <div class="menu-item-title">{item.title}</div>
    {/if}
  </div>
</div>

<style lang="scss">
  .menu-item-container {
    display: flex;
    flex-direction: row;
    padding: 4px 8px;
    cursor: pointer;

    border-radius: 8px;
    margin-bottom: 4px;

    &:last-child {
      margin-bottom: 0;
    }

    &--selected {
      background-color: dodgerblue;
    }
  }

  .menu-item {
    width: 100%;
    margin-left: 8px;
  }

  .menu-item-title {
    font-size: 14px;
    color: #b7b7b7;
    max-width: 85%;
    overflow-wrap: anywhere;

    &--selected {
      color: white;
    }

    &--unread {
      color: white;
      font-weight: 600;
    }
  }
</style>
