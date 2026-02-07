import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiPythonService } from '../../services/api-python.service';

@Component({
  selector: 'app-api-python',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './api-python.component.html',
  styleUrl: './api-python.component.css',
})
export class ApiPythonComponent {
  loading = false;
  result: string | null = null;
  error: string | null = null;

  horizonWeeks = 13;
  productIds = 'BAG-001, BAG-002, BAG-003';

  constructor(private api: ApiPythonService) {}

  get productIdList(): string[] {
    return this.productIds.split(',').map((s) => s.trim()).filter(Boolean);
  }

  callForecast(): void {
    this.startCall();
    const ids = this.productIdList.length ? this.productIdList : ['BAG-001', 'BAG-002'];
    this.api.getForecast(ids, this.horizonWeeks).subscribe((res) => this.finish(res));
  }

  callHealth(): void {
    this.startCall();
    this.api.getHealth().subscribe((res) => this.finish(res));
  }

  callModelMetrics(): void {
    this.startCall();
    this.api.getModelMetrics().subscribe((res) => this.finish(res));
  }

  private startCall(): void {
    this.loading = true;
    this.result = null;
    this.error = null;
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
