import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { getHttpErrorMessage } from '../utils/http-error.util';

@Injectable({ providedIn: 'root' })
export class ApiDotnetService {
  private readonly baseUrl = '/api';

  constructor(private http: HttpClient) {}

  getProductionPlan(collectionId: string, horizonWeeks: number): Observable<unknown> {
    return this.http
      .get(
        `${this.baseUrl}/ProductionPlanning/recommendations/${collectionId}?horizonWeeks=${horizonWeeks}`
      )
      .pipe(catchError((e) => of({ error: getHttpErrorMessage(e) })));
  }

  getForecast(productIds: string[], horizonWeeks: number): Observable<unknown> {
    return this.http
      .post(`${this.baseUrl}/Forecast`, {
        productIds,
        startDate: new Date().toISOString().split('T')[0],
        forecastHorizonWeeks: horizonWeeks,
      })
      .pipe(catchError((e) => of({ error: getHttpErrorMessage(e) })));
  }
}
