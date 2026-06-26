import {
	IDataObject,
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	JsonObject,
	NodeApiError,
	NodeOperationError,
} from 'n8n-workflow';

export class Signatrust implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Signatrust',
		name: 'signatrust',
		icon: 'file:signatrust.svg',
		group: ['transform'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description: 'Generate, verify, and retrieve cryptographically signed AI Decision Receipts using Signatrust.',
		defaults: {
			name: 'Signatrust',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'signatrustApi',
				required: true,
			},
		],
		requestDefaults: {
			baseURL: '={{$credentials.baseUrl}}',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
			},
		},
		properties: [
			// ─── Operation Selector ───────────────────────────────────────────
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'Generate Decision Receipt',
						value: 'generateReceipt',
						action: 'Generate a decision receipt',
						description: 'Create a cryptographically signed receipt for an AI agent decision',
					},
					{
						name: 'Verify Decision Receipt',
						value: 'verifyReceipt',
						action: 'Verify a decision receipt',
						description: 'Verify the authenticity and integrity of an existing receipt',
					},
					{
						name: 'Get Decision Receipt',
						value: 'getReceipt',
						action: 'Get a decision receipt',
						description: 'Retrieve the full details of a receipt by its ID',
					},
				],
				default: 'generateReceipt',
			},

			// ─── Generate Decision Receipt ────────────────────────────────────
			{
				displayName: 'Agent Name',
				name: 'agentName',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. LoanApprovalAgent',
				description: 'The name or identifier of the AI agent that made the decision',
				displayOptions: {
					show: {
						operation: ['generateReceipt'],
					},
				},
			},
			{
				displayName: 'Workflow Name',
				name: 'workflowName',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. Loan Approval Workflow',
				description: 'The name of the n8n workflow in which the decision was made',
				displayOptions: {
					show: {
						operation: ['generateReceipt'],
					},
				},
			},
			{
				displayName: 'Action Taken',
				name: 'action',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. Approved loan application',
				description: 'A short description of the action the AI agent took',
				displayOptions: {
					show: {
						operation: ['generateReceipt'],
					},
				},
			},
			{
				displayName: 'Decision Output',
				name: 'decision',
				type: 'string',
				typeOptions: {
					rows: 4,
				},
				required: true,
				default: '',
				placeholder: 'e.g. {"approved": true, "amount": 50000, "reason": "Credit score above threshold"}',
				description: 'The full output or result returned by the AI agent. Can be a JSON object or plain text.',
				displayOptions: {
					show: {
						operation: ['generateReceipt'],
					},
				},
			},
			{
				displayName: 'Additional Fields',
				name: 'additionalFields',
				type: 'collection',
				placeholder: 'Add Field',
				default: {},
				displayOptions: {
					show: {
						operation: ['generateReceipt'],
					},
				},
				options: [
					{
						displayName: 'Workflow ID',
						name: 'workflowId',
						type: 'string',
						default: '',
						placeholder: 'e.g. workflow_abc123',
						description: 'The unique identifier of the n8n workflow (auto-populated if left empty)',
					},
					{
						displayName: 'Model Used',
						name: 'modelUsed',
						type: 'string',
						default: '',
						placeholder: 'e.g. gpt-4o',
						description: 'The AI model that generated the decision',
					},
					{
						displayName: 'Input Prompt',
						name: 'inputPrompt',
						type: 'string',
						typeOptions: {
							rows: 3,
						},
						default: '',
						description: 'The prompt or input data sent to the AI model',
					},
					{
						displayName: 'Tags',
						name: 'tags',
						type: 'string',
						default: '',
						placeholder: 'e.g. finance, loan, high-value',
						description: 'Comma-separated tags to categorize this receipt',
					},
				],
			},

			// ─── Verify / Get Decision Receipt ───────────────────────────────
			{
				displayName: 'Receipt ID',
				name: 'receiptId',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. rcpt_a1b2c3d4e5f6',
				description: 'The unique identifier of the receipt to verify or retrieve',
				displayOptions: {
					show: {
						operation: ['verifyReceipt', 'getReceipt'],
					},
				},
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		const credentials = await this.getCredentials('signatrustApi');

		const baseUrl = (credentials.baseUrl as string).replace(/\/$/, '');

		for (let i = 0; i < items.length; i++) {
			const operation = this.getNodeParameter('operation', i) as string;

			try {
				let responseData: IDataObject;

				// ─── Generate Decision Receipt ────────────────────────────────
				if (operation === 'generateReceipt') {
					const agentName = this.getNodeParameter('agentName', i) as string;
					const workflowName = this.getNodeParameter('workflowName', i) as string;
					const action = this.getNodeParameter('action', i) as string;
					const decision = this.getNodeParameter('decision', i) as string;
					const additionalFields = this.getNodeParameter('additionalFields', i) as {
						workflowId?: string;
						modelUsed?: string;
						inputPrompt?: string;
						tags?: string;
					};

					const body: Record<string, unknown> = {
						agent_name: agentName,
						workflow_name: workflowName,
						action,
						decision,
					};

					if (additionalFields.workflowId) body.workflow_id = additionalFields.workflowId;
					if (additionalFields.modelUsed) body.model_used = additionalFields.modelUsed;
					if (additionalFields.inputPrompt) body.input_prompt = additionalFields.inputPrompt;
					if (additionalFields.tags) {
						body.tags = additionalFields.tags.split(',').map((t) => t.trim());
					}

					responseData = await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						{
							method: 'POST',
							url: `${baseUrl}/receipts`,
							headers: {
								'Content-Type': 'application/json',
							},
							body,
							json: true,
						},
					) as IDataObject;
				}

				// ─── Verify Decision Receipt ──────────────────────────────────
				else if (operation === 'verifyReceipt') {
					const receiptId = this.getNodeParameter('receiptId', i) as string;

					responseData = await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						{
							method: 'GET',
							url: `${baseUrl}/receipts/${receiptId}/verify`,
							json: true,
						},
					) as IDataObject;
				}

				// ─── Get Decision Receipt ─────────────────────────────────────
				else if (operation === 'getReceipt') {
					const receiptId = this.getNodeParameter('receiptId', i) as string;

					responseData = await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						{
							method: 'GET',
							url: `${baseUrl}/receipts/${receiptId}`,
							json: true,
						},
					) as IDataObject;
				} else {
					throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`);
				}

				returnData.push({
					json: responseData,
					pairedItem: { item: i },
				});
			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: {
							error: (error as Error).message,
						},
						pairedItem: { item: i },
					});
					continue;
				}
				throw new NodeApiError(this.getNode(), error as JsonObject, {
					itemIndex: i,
				});
			}
		}

		return [returnData];
	}
}
