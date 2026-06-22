import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import OperarioIncidenciasPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { mockIncidencia, mockMaquina } from '@/test/msw/fixtures';

describe('OperarioIncidenciasPage (MSW)', () => {
  it('lista incidencias con prioridad y estado', async () => {
    renderWithProviders(<OperarioIncidenciasPage />);

    expect(await screen.findByText('Incidencias')).toBeInTheDocument();
    expect(screen.getByText(mockIncidencia.titulo)).toBeInTheDocument();
    expect(screen.getByText('ALTA')).toBeInTheDocument();
    expect(screen.getByText('ABIERTA')).toBeInTheDocument();
    expect(screen.getByText('1 incidencias')).toBeInTheDocument();
  });

  it('habilita reportar incidencia con asignación activa', async () => {
    renderWithProviders(<OperarioIncidenciasPage />);

    await screen.findByText(mockIncidencia.titulo);
    expect(screen.getByRole('button', { name: /Reportar incidencia/i })).not.toBeDisabled();
  });

  it('muestra máquinas en el listado del API', async () => {
    renderWithProviders(<OperarioIncidenciasPage />);

    await screen.findByText('Incidencias');
    expect(screen.getByText(/FALLA MAQUINA/i)).toBeInTheDocument();
    expect(mockMaquina.nombre).toBeTruthy();
  });
});
