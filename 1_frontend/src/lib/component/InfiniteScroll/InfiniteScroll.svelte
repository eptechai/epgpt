<script lang="ts">
  import { onDestroy, createEventDispatcher } from 'svelte';

  export let threshold = 0;
  export let horizontal = false;
  export let elementScroll: HTMLElement | null = null;
  export let hasMore = true;
  export let reverse = false;

  const dispatch = createEventDispatcher();
  let isLoadMore = false;
  let component: HTMLElement | undefined;
  let beforeScrollHeight: number | undefined;
  let beforeScrollTop: number | undefined;

  $: if (component || elementScroll) {
    const element: HTMLElement = elementScroll
      ? elementScroll
      : ((component as HTMLElement).parentNode as HTMLElement);

    if (reverse) {
      element.scrollTop = element.scrollHeight;
    }

    element.addEventListener('scroll', onScroll);
    element.addEventListener('resize', onScroll);
  }

  $: if (isLoadMore && reverse) {
    const element: HTMLElement = elementScroll
      ? elementScroll
      : ((component as HTMLElement).parentNode as HTMLElement);

    // Note: Wait for the DOM to update
    setTimeout(() => {
      element.scrollTop = element.scrollHeight - (beforeScrollHeight || 0) + (beforeScrollTop || 0);
    }, 100);
  }

  const onScroll = (e: Event) => {
    if (!hasMore) return;

    let offset = 0;

    if (reverse) {
      offset = horizontal
        ? (e.target as HTMLElement).scrollLeft
        : (e.target as HTMLElement).scrollTop;
    } else {
      offset = horizontal
        ? (e.target as HTMLElement).scrollWidth -
          (e.target as HTMLElement).clientWidth -
          (e.target as HTMLElement).scrollLeft
        : (e.target as HTMLElement).scrollHeight -
          (e.target as HTMLElement).clientHeight -
          (e.target as HTMLElement).scrollTop;
    }

    if (offset <= threshold) {
      if (!isLoadMore && hasMore) {
        dispatch('loadMore');
        beforeScrollHeight = (e.target as HTMLElement).scrollHeight;
        beforeScrollTop = (e.target as HTMLElement).scrollTop;
      }
      isLoadMore = true;
    } else {
      isLoadMore = false;
    }
  };

  onDestroy(() => {
    if (component || elementScroll) {
      const element: HTMLElement = elementScroll
        ? elementScroll
        : ((component as HTMLElement).parentNode as HTMLElement);

      element.removeEventListener('scroll', onScroll);
      element.removeEventListener('resize', onScroll);
    }
  });
</script>

<div bind:this={component} style="width:0px" />
