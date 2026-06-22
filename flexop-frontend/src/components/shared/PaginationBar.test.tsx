import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { PaginationBar } from './PaginationBar';

describe('PaginationBar', () => {
  it('muestra resumen cuando hay una sola pagina', () => {
    render(<PaginationBar page={1} total={5} onPageChange={vi.fn()} />);
    expect(screen.getByText('Mostrando 5 de 5')).toBeInTheDocument();
  });

  it('navega a pagina siguiente', async () => {
    const onPageChange = vi.fn();
    const user = userEvent.setup();
    render(
      <PaginationBar page={1} total={45} pageSize={20} onPageChange={onPageChange} />,
    );

    expect(screen.getByText(/Mostrando 1–20 de 45/)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Siguiente/i }));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });
});
