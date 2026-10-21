// Board layout helpers: squares are drawn as a ring on the edge of a square grid.

export type Cell = { row: number; column: number }

/**
 * Grid cell (1-based, CSS grid lines) of a square on a ring of `size` squares.
 * Square 0 sits in the bottom-right corner and play goes clockwise:
 * left along the bottom, up the left side, right along the top, down the right side.
 * A ring of 16 squares fills the edge of a 5x5 grid.
 */
export function ringCell(index: number, size: number): Cell {
  if (size % 4 !== 0) throw new Error('The board size must be a multiple of 4')
  const side = size / 4
  const last = side + 1
  const step = index % side

  switch (Math.floor(index / side)) {
    case 0: // Bottom row, right to left.
      return { row: last, column: last - step }
    case 1: // Left column, bottom to top.
      return { row: last - step, column: 1 }
    case 2: // Top row, left to right.
      return { row: 1, column: 1 + step }
    default: // Right column, top to bottom.
      return { row: 1 + step, column: last }
  }
}

export function gridSize(size: number): number {
  return size / 4 + 1
}
