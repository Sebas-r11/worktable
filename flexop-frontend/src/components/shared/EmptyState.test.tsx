import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Inbox } from 'lucide-react';
import { EmptyState } from './EmptyState';

describe('EmptyState', () => {
  it('renderiza titulo y descripcion', () => {
    render(
      <EmptyState title="Sin datos" description="No hay registros aún" />
    );
    expect(screen.getByText('Sin datos')).toBeInTheDocument();
    expect(screen.getByText('No hay registros aún')).toBeInTheDocument();
  });

  it('renderiza children opcionales', () => {
    render(
      <EmptyState title="Vacío">
        <button type="button">Crear</button>
      </EmptyState>
    );
    expect(screen.getByRole('button', { name: 'Crear' })).toBeInTheDocument();
  });

  it('acepta icono sin romper layout', () => {
    const { container } = render(
      <EmptyState title="Bandeja vacía" icon={Inbox} />
    );
    expect(container.querySelector('svg')).toBeTruthy();
  });
});
