import type { Conversation } from '$lib/model/conversation';

export enum MenuItemType {
  Conversation = 'Conversation',
  Badge = 'Badge'
}

export interface ConversationMenuItem {
  type: MenuItemType.Conversation;
  conversation: Conversation;
}
export function ConversationMenuItem(conversation: Conversation): ConversationMenuItem {
  return {
    type: MenuItemType.Conversation,
    conversation
  };
}

export interface BadgeMenuItem {
  type: MenuItemType.Badge;
  title: string;
}
export function BadgeMenuItem(title: string): BadgeMenuItem {
  return {
    type: MenuItemType.Badge,
    title
  };
}

export type MenuItem = ConversationMenuItem | BadgeMenuItem;
