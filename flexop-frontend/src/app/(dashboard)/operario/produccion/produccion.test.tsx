import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import OperarioProduccionPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { mockRegistroProduccion } from '@/test/msw/fixtures';

describe('OperarioProduccionPage (MSW)', () => {
  it('lista registros de producción', async () => {
    renderWithProviders(<OperarioProduccionPage />);

    expect(await screen.findByText('Registro de Producción')).toBeInTheDocument();
    expect(screen.getByText(String(mockRegistroProduccion.cantidad))).toBeInTheDocument();
    expect(screen.getByText('Turno mañana')).toBeInTheDocument();
    expect(screen.getByText('1 registros')).toBeInTheDocument();
  });

  it('habilita registrar con asignación activa', async () => {
    renderWithProviders(<OperarioProduccionPage />);

    await screen.findByText('Registro de Producción');
    const registrar = screen.getByRole('button', { name: /Registrar/i });
    expect(registrar).not.toBeDisabled();
    expect(
      screen.queryByText(/Necesitas una asignación activa/i),
    ).not.toBeInTheDocument();
  });
});
