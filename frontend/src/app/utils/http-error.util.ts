/**
 * Message d'erreur utilisateur à partir d'une erreur HTTP / réseau.
 */
export function getHttpErrorMessage(err: unknown): string {
  const msg = (err as any)?.message ?? '';
  const status = (err as any)?.status ?? (err as any)?.error?.status;
  if (status === 0 || /fetch|network|failed|connection|refused|aggregateerror/i.test(msg)) {
    return "Service injoignable. Vérifiez que le backend est démarré (API .NET: port 5000, API Python: port 8000).";
  }
  return (err as any)?.error?.message ?? (msg || 'Erreur inconnue');
}
