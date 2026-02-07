import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiDotnetService } from '../../services/api-dotnet.service';

@Component({
  selector: 'app-api-dotnet',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './api-dotnet.component.html',
  styleUrl: './api-dotnet.component.css',
})
export class ApiDotnetComponent {
  loading = false;
  result: string | null = null;
  error: string | null = null;

  collectionId = 'Spring2024';
  horizonWeeks = 13;
  productIds = 'BAG-001, BAG-002, BAG-003';

  constructor(private api: ApiDotnetService) {}

  get productIdList(): string[] {
    return this.productIds.split(',').map((s) => s.trim()).filter(Boolean);
  }

  callProductionPlan(): void {
    this.startCall();
    this.api.getProductionPlan(this.collectionId, this.horizonWeeks).subscribe((res) => this.finish(res));
  }

  callForecast(): void {
    this.startCall();
    const ids = this.productIdList.length ? this.productIdList : ['BAG-001', 'BAG-002'];
    this.api.getForecast(ids, this.horizonWeeks).subscribe((res) => this.finish(res));
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
