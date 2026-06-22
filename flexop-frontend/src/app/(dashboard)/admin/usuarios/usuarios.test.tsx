import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import AdminUsuariosPage from './page';
import { renderWithProviders } from '@/test/test-utils';
import { mockUsuarioGerente, mockUsuarioOperario } from '@/test/msw/fixtures';

describe('AdminUsuariosPage (MSW)', () => {
  it('lista usuarios con rol y estado', async () => {
    renderWithProviders(<AdminUsuariosPage />);

    expect(await screen.findByText('Usuarios')).toBeInTheDocument();
    expect(screen.getByText(mockUsuarioOperario.username)).toBeInTheDocument();
    expect(screen.getByText(`${mockUsuarioOperario.first_name} ${mockUsuarioOperario.last_name}`)).toBeInTheDocument();
    expect(screen.getByText('OPERARIO')).toBeInTheDocument();
    expect(screen.getByText(mockUsuarioGerente.username)).toBeInTheDocument();
    expect(screen.getByText('GERENTE')).toBeInTheDocument();
  });

  it('filtra usuarios por búsqueda', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminUsuariosPage />);

    await screen.findByText(mockUsuarioOperario.username);
    const search = screen.getByPlaceholderText(/Buscar por usuario/i);
    await user.type(search, 'gerente');

    expect(screen.queryByText(mockUsuarioOperario.username)).not.toBeInTheDocument();
    expect(screen.getByText(mockUsuarioGerente.username)).toBeInTheDocument();
  });

  it('abre el diálogo de nuevo usuario', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdminUsuariosPage />);

    await screen.findByText('Usuarios');
    await user.click(screen.getByRole('button', { name: /Nuevo usuario/i }));

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Nuevo usuario' })).toBeInTheDocument();
  });
});
