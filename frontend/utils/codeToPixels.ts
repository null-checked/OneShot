/**
 * Convert code to pixel representation for visualization
 * Uses token-based coloring approach
 */

export interface Pixel {
  color: string;
  type: string;
}

// Token types and their colors
const TOKEN_COLORS = {
  keyword: '#3498db',      // blue
  string: '#2ecc71',       // green
  number: '#e67e22',       // orange
  operator: '#9b59b6',     // purple
  comment: '#7f8c8d',      // gray
  identifier: '#ecf0f1',   // light gray
  whitespace: 'transparent',
  punctuation: '#95a5a6',  // medium gray
  function: '#1abc9c',     // teal
} as const;

// Python keywords
const PYTHON_KEYWORDS = new Set([
  'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
  'import', 'from', 'as', 'try', 'except', 'finally', 'with',
  'lambda', 'yield', 'pass', 'break', 'continue', 'in', 'is',
  'and', 'or', 'not', 'True', 'False', 'None', 'async', 'await'
]);

// Operators
const OPERATORS = new Set([
  '+', '-', '*', '/', '//', '%', '**', '==', '!=', '<', '>', '<=', '>=',
  '=', '+=', '-=', '*=', '/=', '&', '|', '^', '~', '<<', '>>'
]);

/**
 * Simple tokenizer for Python code
 */
function tokenize(code: string): { type: string; value: string }[] {
  const tokens: { type: string; value: string }[] = [];
  let i = 0;

  while (i < code.length) {
    const char = code[i];

    // Comments
    if (char === '#') {
      let value = '';
      while (i < code.length && code[i] !== '\n') {
        value += code[i];
        i++;
      }
      tokens.push({ type: 'comment', value });
      continue;
    }

    // Strings (single or double quotes)
    if (char === '"' || char === "'") {
      const quote = char;
      let value = char;
      i++;
      let escaped = false;

      while (i < code.length) {
        const c = code[i];
        value += c;

        if (c === '\\' && !escaped) {
          escaped = true;
        } else if (c === quote && !escaped) {
          i++;
          break;
        } else {
          escaped = false;
        }
        i++;
      }
      tokens.push({ type: 'string', value });
      continue;
    }

    // Numbers
    if (/\d/.test(char)) {
      let value = '';
      while (i < code.length && /[\d.]/.test(code[i])) {
        value += code[i];
        i++;
      }
      tokens.push({ type: 'number', value });
      continue;
    }

    // Whitespace
    if (/\s/.test(char)) {
      let value = '';
      while (i < code.length && /\s/.test(code[i])) {
        value += code[i];
        i++;
      }
      tokens.push({ type: 'whitespace', value });
      continue;
    }

    // Operators (multi-char)
    if (OPERATORS.has(char + code[i + 1])) {
      tokens.push({ type: 'operator', value: char + code[i + 1] });
      i += 2;
      continue;
    }

    // Operators (single-char)
    if (OPERATORS.has(char) || '()[]{}:,'.includes(char)) {
      tokens.push({ type: char === '(' || char === ')' ? 'punctuation' : 'operator', value: char });
      i++;
      continue;
    }

    // Identifiers and keywords
    if (/[a-zA-Z_]/.test(char)) {
      let value = '';
      while (i < code.length && /[a-zA-Z0-9_]/.test(code[i])) {
        value += code[i];
        i++;
      }

      // Check if it's a keyword
      if (PYTHON_KEYWORDS.has(value)) {
        tokens.push({ type: 'keyword', value });
      } else {
        // Check if next non-whitespace is '(' to identify functions
        let j = i;
        while (j < code.length && /\s/.test(code[j])) j++;
        if (code[j] === '(') {
          tokens.push({ type: 'function', value });
        } else {
          tokens.push({ type: 'identifier', value });
        }
      }
      continue;
    }

    // Default: treat as punctuation
    tokens.push({ type: 'punctuation', value: char });
    i++;
  }

  return tokens;
}

/**
 * Convert code to 2D pixel array
 */
export function codeToPixels(code: string, maxWidth: number = 60): Pixel[][] {
  const tokens = tokenize(code);
  const pixels: Pixel[][] = [];
  let currentRow: Pixel[] = [];

  for (const token of tokens) {
    // Handle newlines
    if (token.value.includes('\n')) {
      const lines = token.value.split('\n');
      for (let i = 0; i < lines.length; i++) {
        if (i > 0) {
          pixels.push([...currentRow]);
          currentRow = [];
        }

        // Add a pixel for each character in the line
        for (let j = 0; j < lines[i].length; j++) {
          currentRow.push({
            color: TOKEN_COLORS[token.type as keyof typeof TOKEN_COLORS] || TOKEN_COLORS.identifier,
            type: token.type
          });
        }
      }
      continue;
    }

    // Add token characters to current row
    for (let i = 0; i < token.value.length; i++) {
      currentRow.push({
        color: TOKEN_COLORS[token.type as keyof typeof TOKEN_COLORS] || TOKEN_COLORS.identifier,
        type: token.type
      });

      // Wrap if exceeds max width
      if (currentRow.length >= maxWidth) {
        pixels.push([...currentRow]);
        currentRow = [];
      }
    }
  }

  // Push last row if not empty
  if (currentRow.length > 0) {
    pixels.push(currentRow);
  }

  return pixels;
}

/**
 * Get a simplified version of pixels for smaller displays
 */
export function simplifyPixels(pixels: Pixel[][], targetRows: number = 20): Pixel[][] {
  if (pixels.length <= targetRows) {
    return pixels;
  }

  const simplified: Pixel[][] = [];
  const step = pixels.length / targetRows;

  for (let i = 0; i < targetRows; i++) {
    const idx = Math.floor(i * step);
    simplified.push(pixels[idx]);
  }

  return simplified;
}
