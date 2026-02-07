import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';

export type ApiBackend = 'dotnet' | 'python';

@Injectable({ providedIn: 'root' })
export class ApiCallerService {
  private dotnetBase = '/api';
  private pythonBase = '/python-api';

  constructor(private http: HttpClient) {}

  /** Appel API .NET : plan de production */
  callDotNetProductionPlan(collectionId: string, horizonWeeks: number): Observable<unknown> {
    return this.http.get(
      `${this.dotnetBase}/ProductionPlanning/recommendations/${collectionId}?horizonWeeks=${horizonWeeks}`
    ).pipe(catchError((e) => of({ error: this.getErrorMessage(e) })));
  }

  /** Appel API .NET : prévisions (POST) */
  callDotNetForecast(productIds: string[], horizonWeeks: number): Observable<unknown> {
    return this.http.post(`${this.dotnetBase}/Forecast`, {
      productIds,
      startDate: new Date().toISOString().split('T')[0],
      forecastHorizonWeeks: horizonWeeks,
    }).pipe(catchError((e) => of({ error: this.getErrorMessage(e) })));
  }

  /** Appel API Python : forecast */
  callPythonForecast(productIds: string[], horizonWeeks: number): Observable<unknown> {
    return this.http.post(`${this.pythonBase}/forecast`, {
      product_ids: productIds,
      start_date: new Date().toISOString().split('T')[0],
      forecast_horizon_weeks: horizonWeeks,
      channel: 'All',
      countries: ['All'],
    }).pipe(catchError((e) => of({ error: this.getErrorMessage(e) })));
  }

  /** Appel API Python : health */
  callPythonHealth(): Observable<unknown> {
    return this.http.get(`${this.pythonBase}/health`).pipe(
      catchError((e) => of({ error: this.getErrorMessage(e) }))
    );
  }

  /** Appel API Python : métriques modèle */
  callPythonModelMetrics(): Observable<unknown> {
    return this.http.get(`${this.pythonBase}/model/metrics`).pipe(
      catchError((e) => of({ error: this.getErrorMessage(e) }))
    );
  }

  private getErrorMessage(err: unknown): string {
    const msg = (err as any)?.message ?? '';
    const status = (err as any)?.status ?? (err as any)?.error?.status;
    if (status === 0 || /fetch|network|failed|connection|refused|aggregateerror/i.test(msg)) {
      return "Service injoignable. Vérifiez que le backend est démarré (API .NET: port 5000, API Python: port 8000).";
    }
    return (err as any)?.error?.message ?? (msg || 'Erreur inconnue');
  }
}
