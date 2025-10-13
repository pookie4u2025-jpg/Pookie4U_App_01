/**
 * Daily love message rotation utility
 * Rotates messages based on relationship_mode and current date at local midnight
 */

import { getLocalMidnight } from './DateFormatter';

export interface LoveMessage {
  id: string;
  text: string;
  category: string;
  relationship_mode?: string;
}

// Generate deterministic index based on user ID and date
export const getDailyMessageIndex = (userId: string, messages: LoveMessage[], date?: Date): number => {
  const targetDate = date || new Date();
  const midnight = getLocalMidnight(targetDate);
  
  // Create a seed based on user ID and date (YYYY-MM-DD format)
  const dateStr = midnight.toISOString().split('T')[0]; // YYYY-MM-DD
  const seedString = `${userId}-${dateStr}`;
  
  // Simple hash function for deterministic pseudo-random selection
  let hash = 0;
  for (let i = 0; i < seedString.length; i++) {
    const char = seedString.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Ensure positive index
  const positiveHash = Math.abs(hash);
  
  return positiveHash % messages.length;
};

// Filter messages based on relationship mode
export const filterMessagesByRelationshipMode = (
  messages: LoveMessage[],
  relationshipMode: string
): LoveMessage[] => {
  return messages.filter(message => {
    // If message doesn't specify a mode, it's universal
    if (!message.relationship_mode) {
      return true;
    }
    
    // Match the specific relationship mode
    return message.relationship_mode === relationshipMode;
  });
};

// Get daily message for a specific user and relationship mode
export const getDailyMessage = (
  userId: string,
  allMessages: LoveMessage[],
  relationshipMode: string,
  date?: Date
): LoveMessage | null => {
  // Filter messages for the relationship mode
  const filteredMessages = filterMessagesByRelationshipMode(allMessages, relationshipMode);
  
  if (filteredMessages.length === 0) {
    return null;
  }
  
  // Get deterministic index for the day
  const index = getDailyMessageIndex(userId, filteredMessages, date);
  
  return filteredMessages[index];
};

// Check if message has changed since last retrieval (for notifications)
export const hasMessageChanged = (
  userId: string,
  messages: LoveMessage[],
  relationshipMode: string,
  lastCheckedDate: Date
): boolean => {
  const todayMessage = getDailyMessage(userId, messages, relationshipMode);
  const yesterdayMessage = getDailyMessage(userId, messages, relationshipMode, lastCheckedDate);
  
  return todayMessage?.id !== yesterdayMessage?.id;
};

// Get message for a specific category and relationship mode
export const getDailyMessageByCategory = (
  userId: string,
  allMessages: LoveMessage[],
  relationshipMode: string,
  category: string,
  date?: Date
): LoveMessage | null => {
  // Filter by both relationship mode and category
  const filteredMessages = allMessages.filter(message => {
    const modeMatch = !message.relationship_mode || message.relationship_mode === relationshipMode;
    const categoryMatch = message.category === category;
    return modeMatch && categoryMatch;
  });
  
  if (filteredMessages.length === 0) {
    return null;
  }
  
  const index = getDailyMessageIndex(`${userId}-${category}`, filteredMessages, date);
  return filteredMessages[index];
};

// Utility to get time until next message rotation (midnight)
export const getTimeUntilNextRotation = (): number => {
  const now = new Date();
  const nextMidnight = new Date(now);
  nextMidnight.setDate(nextMidnight.getDate() + 1);
  nextMidnight.setHours(0, 0, 0, 0);
  
  return nextMidnight.getTime() - now.getTime();
};

// Categories for different message types
export const MESSAGE_CATEGORIES = {
  GOOD_MORNING: 'good_morning',
  GOOD_NIGHT: 'good_night',
  LOVE_CONFESSION: 'love_confession',
  APOLOGY: 'apology',
  FUNNY_HINGLISH: 'funny_hinglish',
  ENCOURAGEMENT: 'encouragement',
  ROMANTIC: 'romantic',
  APPRECIATION: 'appreciation',
} as const;

// Relationship modes
export const RELATIONSHIP_MODES = {
  SAME_HOME: 'SAME_HOME',
  DAILY_IRL: 'DAILY_IRL',
  LONG_DISTANCE: 'LONG_DISTANCE',
} as const;

export type MessageCategory = typeof MESSAGE_CATEGORIES[keyof typeof MESSAGE_CATEGORIES];
export type RelationshipMode = typeof RELATIONSHIP_MODES[keyof typeof RELATIONSHIP_MODES];