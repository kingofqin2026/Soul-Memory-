/**
 * Soul Memory Plugin for OpenClaw
 * 
 * Automatically injects Soul Memory search results before each response
 * using the before_prompt_build Hook.
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Soul Memory configuration
interface SoulMemoryConfig {
  enabled: boolean;
  topK: number;
  minScore: number;
}

// Search result from Soul Memory
interface MemoryResult {
  path: string;
  content: string;
  score: number;
  priority?: string;
}

/**
 * Search Soul Memory using Python backend
 */
async function searchMemories(query: string, config: SoulMemoryConfig): Promise<MemoryResult[]> {
  try {
    const { stdout } = await execAsync(
      `python3 /root/.openclaw/workspace/soul-memory/cli.py search "${query}" --top_k ${config.topK} --min_score ${config.minScore}`,
      { timeout: 5000 } // 5 second timeout
    );

    // Parse JSON output
    const results = JSON.parse(stdout || '[]');
    return Array.isArray(results) ? results : [];
  } catch (error) {
    // Silently fail on errors to avoid breaking the agent
    console.error('[Soul Memory] Search failed:', error instanceof Error ? error.message : String(error));
    return [];
  }
}

/**
 * Build memory context string from results
 */
function buildMemoryContext(results: MemoryResult[]): string {
  if (results.length === 0) {
    return '';
  }

  let context = '\n## 🧠 Memory Context\n\n';
  
  results.forEach((result, index) => {
    const scoreBadge = result.score > 5 ? '🔥' : result.score > 3 ? '⭐' : '';
    const priorityBadge = result.priority === 'C' ? '[🔴 Critical]' 
                        : result.priority === 'I' ? '[🟡 Important]' 
                        : '';
    
    context += `${index + 1}. ${scoreBadge} ${priorityBadge} ${result.content}\n`;
    
    if (result.path && result.score > 3) {
      context += `   *Source: ${result.path}*\n`;
    }
    context += '\n';
  });

  return context;
}

/**
 * Get the last user message from the conversation
 */
function getLastUserMessage(messages: any[]): string {
  if (!messages || messages.length === 0) {
    return '';
  }

  // Find the last message from user role
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.role === 'user' && msg.content) {
      // Handle different content formats
      if (Array.isArray(msg.content)) {
        return msg.content
          .filter((item: any) => item.type === 'text')
          .map((item: any) => item.text)
          .join(' ');
      } else if (typeof msg.content === 'string') {
        return msg.content;
      }
    }
  }

  return '';
}

/**
 * Extract query from user message, removing metadata blocks
 */
function extractQuery(rawMessage: string): string {
  if (!rawMessage) return '';

  let cleaned = rawMessage.trim();

  // Remove "## 🧠 Memory Context" block and all numbered items under it
  // This matches the header and all numbered list items that follow
  cleaned = cleaned.replace(/## 🧠 Memory Context[\s\S]*?(?=\n\n[A-Z]|$)/g, '').trim();

  // Remove any remaining numbered list items that look like memory entries
  cleaned = cleaned.replace(/^\d+\. 🔥.*$/gm, '');

  // Remove "Conversation info" metadata blocks
  cleaned = cleaned.replace(/Conversation info \(untrusted metadata\):[\s\S]*?\n\n/g, '');

  // Remove "System:" messages
  cleaned = cleaned.replace(/^System: \[[\s\S]*?\]$/gm, '');

  // Remove Markdown code blocks (```json ... ```, ``` ... ```)
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '');

  // Remove HTML/XML-like blocks
  cleaned = cleaned.replace(/<[\s\S]*?>/g, '');

  // Remove empty lines and clean up
  cleaned = cleaned.replace(/\n\s*\n/g, '\n').trim();

  // If after cleaning we have nothing, use a longer prefix of the original message
  if (cleaned.length < 5 && rawMessage.length > 10) {
    // Try to extract the first meaningful sentence
    const firstSentenceMatch = rawMessage.match(/^[^。!！?？\n]+[。!！?？]?/);
    if (firstSentenceMatch) {
      cleaned = firstSentenceMatch[0].trim();
    } else {
      // Fallback to first 200 characters
      cleaned = rawMessage.substring(0, 200).trim();
    }
  }

  // Limit to 200 characters
  return cleaned.substring(0, 200);
}

/**
 * Plugin entry point
 */
export default function register(api: any) {
  const logger = api.logger || console;

  logger.info('[Soul Memory] Plugin registered via api.register()');

  // Register before_prompt_build Hook using api.on() (Plugin Hook API)
  api.on('before_prompt_build', async (event: any, ctx: any) => {
    const config: SoulMemoryConfig = {
      enabled: true,
      topK: 5,
      minScore: 0.0,
      ...api.config.plugins?.entries?.['soul-memory']?.config
    };

    // IMPORTANT: Log that hook was called
    logger.info('[Soul Memory] ✓ BEFORE_PROMPT_BUILD HOOK CALLED via api.on()');
    logger.debug(`[Soul Memory] Config: enabled=${config.enabled}, topK=${config.topK}, minScore=${config.minScore}`);
    logger.debug(`[Soul Memory] Event: prompt=${event.prompt?.substring(0, 50)}..., messages=${event.messages?.length || 0}`);
    logger.debug(`[Soul Memory] Context: agentId=${ctx.agentId}, sessionKey=${ctx.sessionKey}`);

    // Check if enabled
    if (!config.enabled) {
      logger.info('[Soul Memory] Plugin disabled, skipping');
      return {};
    }

    // Get last user message from event.messages
    const messages = event.messages || [];
    const lastUserMessage = getLastUserMessage(messages);

    logger.debug(`[Soul Memory] Last user message length: ${lastUserMessage.length}`);

    // Skip if no user message
    if (!lastUserMessage || lastUserMessage.trim().length === 0) {
      logger.debug('[Soul Memory] No user message found, skipping');
      return {};
    }

    // Extract query with metadata removal
    const query = extractQuery(lastUserMessage);

    // Skip if query is too short
    if (query.length < 5) {
      logger.debug(`[Soul Memory] Query too short (${query.length} chars): "${query}", skipping`);
      return {};
    }

    logger.info(`[Soul Memory] Searching for: "${query}"`);

    // Search memories
    const results = await searchMemories(query, config);

    logger.info(`[Soul Memory] Found ${results.length} results`);

    if (results.length === 0) {
      logger.info('[Soul Memory] No memories found');
      return {};
    }

    // Build memory context
    const memoryContext = buildMemoryContext(results);

    logger.info(`[Soul Memory] Injected ${results.length} memories into prompt (${memoryContext.length} chars)`);

    // Return with prependContext
    return {
      prependContext: memoryContext
    };
  });

  logger.info('[Soul Memory] Hook registered via api.on(): before_prompt_build');
}
