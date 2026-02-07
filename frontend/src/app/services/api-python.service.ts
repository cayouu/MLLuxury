import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { getHttpErrorMessage } from '../utils/http-error.util';

@Injectable({ providedIn: 'root' })
export class ApiPythonService {
  private readonly baseUrl = '/python-api';

  constructor(private http: HttpClient) {}

  getForecast(productIds: string[], horizonWeeks: number): Observable<unknown> {
    return this.http
      .post(`${this.baseUrl}/forecast`, {
        product_ids: productIds,
        start_date: new Date().toISOString().split('T')[0],
        forecast_horizon_weeks: horizonWeeks,
        channel: 'All',
        countries: ['All'],
      })
      .pipe(catchError((e) => of({ error: getHttpErrorMessage(e) })));
  }

  getHealth(): Observable<unknown> {
    return this.http
      .get(`${this.baseUrl}/health`)
      .pipe(catchError((e) => of({ error: getHttpErrorMessage(e) })));
  }

  getModelMetrics(): Observable<unknown> {
    return this.http
      .get(`${this.baseUrl}/model/metrics`)
      .pipe(catchError((e) => of({ error: getHttpErrorMessage(e) })));
  }
}
