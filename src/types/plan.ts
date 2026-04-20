export type PlanStatus = "completed" | "in_progress" | "planned";

export interface PlanItem {
	id: string;
	title: string;
	description: string;
	status: PlanStatus;
	createdAt: string;
	updatedAt?: string;
	tags?: string[];
	link?: string;
	likes: number;
}

export interface PlanConfig {
	plans: PlanItem[];
}
