import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiCallerService, ApiBackend } from '../../services/api-caller.service';

type DotNetAction = 'production-plan' | 'forecast';
type PythonAction = 'forecast' | 'health' | 'model-metrics';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  selectedApi: ApiBackend = 'dotnet';
  dotnetAction: DotNetAction = 'production-plan';
  pythonAction: PythonAction = 'forecast';
  loading = false;
  result: string | null = null;
  error: string | null = null;

  collectionId = 'Spring2024';
  horizonWeeks = 13;
  productIds = 'BAG-001, BAG-002, BAG-003';

  constructor(private api: ApiCallerService) {}

  get productIdList(): string[] {
    return this.productIds.split(',').map((s) => s.trim()).filter(Boolean);
  }

  callApi(): void {
    this.loading = true;
    this.result = null;
    this.error = null;

    if (this.selectedApi === 'dotnet') {
      this.callDotNet();
    } else {
      this.callPython();
    }
  }

  private callDotNet(): void {
    if (this.dotnetAction === 'production-plan') {
      this.api.callDotNetProductionPlan(this.collectionId, this.horizonWeeks).subscribe((res) => {
        this.finish(res);
      });
    } else {
      const ids = this.productIdList.length ? this.productIdList : ['BAG-001', 'BAG-002'];
      this.api.callDotNetForecast(ids, this.horizonWeeks).subscribe((res) => {
        this.finish(res);
      });
    }
  }

  private callPython(): void {
    if (this.pythonAction === 'forecast') {
      const ids = this.productIdList.length ? this.productIdList : ['BAG-001', 'BAG-002'];
      this.api.callPythonForecast(ids, this.horizonWeeks).subscribe((res) => this.finish(res));
    } else if (this.pythonAction === 'health') {
      this.api.callPythonHealth().subscribe((res) => this.finish(res));
    } else {
      this.api.callPythonModelMetrics().subscribe((res) => this.finish(res));
    }
  }

  private finish(res: unknown): void {
    this.loading = false;
    if (res && typeof res === 'object' && 'error' in res && typeof (res as any).error === 'string') {
      this.error = (res as any).error;
      return;
    }
    this.result = JSON.stringify(res, null, 2);
  }
}
