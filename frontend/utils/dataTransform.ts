/**
 * Data transformation utilities
 * Convert backend API responses to frontend types
 */

import {
  RecordItem,
  RecordSource,
  MoodItem,
  MoodType,
  InspirationItem,
  TodoItem,
  TodoCategory
} from '../types';

/**
 * Convert backend record to frontend RecordItem
 */
export function transformRecord(record: any): RecordItem {
  return {
    id: record.record_id,
    content: record.original_text,
    createdAt: new Date(record.timestamp).getTime(),
    sourceType: record.input_type === 'audio' ? RecordSource.VOICE : RecordSource.MANUAL
  };
}

/**
 * Convert backend mood type to frontend MoodType
 */
export function transformMoodType(type?: string): MoodType {
  if (!type) return MoodType.CALM;
  
  const typeMap: Record<string, MoodType> = {
    '开心': MoodType.HAPPY,
    '快乐': MoodType.HAPPY,
    '平静': MoodType.CALM,
    '冷静': MoodType.CALM,
    '疲惫': MoodType.TIRED,
    '累': MoodType.TIRED,
    '焦虑': MoodType.ANXIOUS,
    '紧张': MoodType.ANXIOUS,
    '希望': MoodType.HOPEFUL,
    '期待': MoodType.HOPEFUL,
  };

  return typeMap[type] || MoodType.CALM;
}

/**
 * Convert backend mood to frontend MoodItem
 */
export function transformMood(mood: any, index: number): MoodItem {
  // Generate pseudo-random position based on timestamp
  const timestamp = new Date(mood.timestamp).getTime();
  const x = 20 + ((timestamp + index * 13) % 60);
  const y = 20 + ((timestamp + index * 17) % 60);
  
  return {
    id: mood.record_id,
    type: transformMoodType(mood.type),
    date: new Date(mood.timestamp).getTime(),
    intensity: mood.intensity ? mood.intensity / 10 : 0.5,
    x,
    y
  };
}

/**
 * Convert backend inspiration to frontend InspirationItem
 */
export function transformInspiration(inspiration: any): InspirationItem {
  return {
    id: inspiration.record_id,
    content: inspiration.core_idea,
    createdAt: new Date(inspiration.timestamp).getTime(),
    tags: inspiration.tags || []
  };
}

/**
 * Convert backend category to frontend TodoCategory
 */
export function transformTodoCategory(category?: string): TodoCategory {
  const categoryMap: Record<string, TodoCategory> = {
    '工作': 'work',
    '生活': 'life',
    '学习': 'study',
    '健康': 'health'
  };

  return (categoryMap[category || ''] || 'life') as TodoCategory;
}

/**
 * Convert backend todo to frontend TodoItem
 */
export function transformTodo(todo: any): TodoItem {
  const createdAt = new Date(todo.timestamp).getTime();
  
  // Try to parse time if available
  let scheduledAt: number | undefined;
  if (todo.time) {
    // Simple heuristic: if time contains "明天", add 1 day
    if (todo.time.includes('明天')) {
      scheduledAt = createdAt + 24 * 60 * 60 * 1000;
    } else if (todo.time.includes('今天')) {
      scheduledAt = createdAt;
    }
  }

  return {
    id: todo.record_id,
    title: todo.task,
    createdAt,
    scheduledAt,
    isDone: todo.status === 'completed' || todo.status === 'done',
    category: transformTodoCategory(todo.category),
    location: todo.location || undefined,
    time: todo.time || undefined
  };
}
