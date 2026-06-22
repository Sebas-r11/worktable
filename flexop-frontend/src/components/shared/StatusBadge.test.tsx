import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('muestra el valor por defecto', () => {
    render(<StatusBadge value="ACTIVA" />);
    expect(screen.getByText('ACTIVA')).toBeInTheDocument();
  });

  it('muestra label personalizado', () => {
    render(<StatusBadge value="PENDIENTE" label="Pendiente" />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });
});
