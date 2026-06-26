import {
	IDataObject,
	IExecuteFunctions,
	IHttpRequestOptions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	JsonObject,
	NodeApiError,
	NodeConnectionTypes,
	NodeOperationError,
} from 'n8n-workflow';

export class Signatrust implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Signatrust',
		name: 'signatrust',
		icon: { light: 'file:signatrust.svg', dark: 'file:signatrust.dark.svg' },
		group: ['transform'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description:
			'Generate, verify, and retrieve cryptographically signed AI Decision Receipts (Ed25519) using Signatrust. Cloud or self-hosted.',
		defaults: {
			name: 'Signatrust',
		},
		usableAsTool: true,
		inputs: [NodeConnectionTypes.Main],
		outputs: [NodeConnectionTypes.Main],
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
			// ─── Operation Selector ─────────────────────────────────────────
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
						description:
							'Cryptographically seal an AI decision into a Signatrust Decision Receipt',
					},
					{
						name: 'Get Decision Receipt',
						value: 'getReceipt',
						action: 'Get a decision receipt',
						description: 'Retrieve the full details of a receipt by its ID',
					},
					{
						name: 'Verify Decision Receipt',
						value: 'verifyReceipt',
						action: 'Verify a decision receipt',
						description: 'Verify the authenticity and integrity of an existing receipt',
					},
				],
				default: 'generateReceipt',
			},

			// ─── Generate Decision Receipt ──────────────────────────────────
			{
				displayName: 'Agent Name',
				name: 'agentName',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. LoanApprovalAgent',
				description: 'Display name of the AI agent that made the decision',
				displayOptions: { show: { operation: ['generateReceipt'] } },
			},
			{
				displayName: 'Workflow Name',
				name: 'workflowName',
				type: 'string',
				required: true,
				default: '={{$workflow.name}}',
				description: 'Name of the n8n workflow in which the decision was made',
				displayOptions: { show: { operation: ['generateReceipt'] } },
			},
			{
				displayName: 'Action Taken',
				name: 'action',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. Approved loan application',
				description: 'Short description of the action the AI agent took',
				displayOptions: { show: { operation: ['generateReceipt'] } },
			},
			{
				displayName: 'Decision Output',
				name: 'decision',
				type: 'string',
				typeOptions: { rows: 4 },
				required: true,
				default: '',
				placeholder: '={{$json.message.content}}',
				description:
					'The output or result returned by the AI agent (JSON or plain text). Only its SHA-256 hash is stored unless you opt into raw retention.',
				displayOptions: { show: { operation: ['generateReceipt'] } },
			},
			{
				displayName: 'Additional Fields',
				name: 'additionalFields',
				type: 'collection',
				placeholder: 'Add Field',
				default: {},
				displayOptions: { show: { operation: ['generateReceipt'] } },
				// IMPORTANT: collection items must stay alphabetised by displayName
				// to satisfy the `node-param-collection-type-unsorted-items` lint
				// rule used by the n8n verified-node pipeline.
				options: [
					{
						displayName: 'AI Model',
						name: 'modelUsed',
						type: 'string',
						default: '',
						placeholder: 'e.g. gpt-4o',
						description: 'AI model that generated the decision (recorded in the receipt)',
					},
					{
						displayName: 'AI Model Version',
						name: 'modelVersion',
						type: 'string',
						default: '',
						placeholder: 'e.g. 2025-08-01',
						description: 'Version tag of the AI model that generated the decision',
					},
					{
						displayName: 'AI Provider',
						name: 'modelProvider',
						type: 'string',
						default: '',
						placeholder: 'e.g. openai, anthropic, google',
						description: 'AI provider that hosts the model',
					},
					{
						displayName: 'Decision Type',
						name: 'decisionType',
						type: 'string',
						default: '',
						placeholder: 'e.g. loan_decision, refund_approval, deploy_action',
						description: 'A semantic label categorising the decision',
					},
					{
						displayName: 'Human Review Took Place',
						name: 'humanReview',
						type: 'boolean',
						default: false,
						description: 'Whether a human reviewed the decision before it was finalised',
					},
					{
						displayName: 'Include Raw Decision in Metadata',
						name: 'includeDecisionInMetadata',
						type: 'boolean',
						default: false,
						description:
							'Whether to also store the raw decision text inside the receipt metadata. Off by default (privacy-first: only the SHA-256 hash is stored).',
					},
					{
						displayName: 'Input / Prompt',
						name: 'inputPrompt',
						type: 'string',
						typeOptions: { rows: 3 },
						default: '',
						description: 'The prompt or input sent to the AI model. Only its SHA-256 hash is stored.',
					},
					{
						displayName: 'Permissions Used',
						name: 'permissions',
						type: 'string',
						default: '',
						placeholder: 'credit.decide, payments.execute',
						description: 'Comma-separated permissions the agent exercised to make this decision',
					},
					{
						displayName: 'Policies',
						name: 'policies',
						type: 'string',
						default: '',
						placeholder: 'eu-ai-act-high-risk, internal-credit-v3',
						description: 'Comma-separated list of policies that govern this decision',
					},
					{
						displayName: 'Risk Level',
						name: 'riskLevel',
						type: 'options',
						options: [
							{ name: 'Critical', value: 'critical' },
							{ name: 'High', value: 'high' },
							{ name: 'Low', value: 'low' },
							{ name: 'Medium', value: 'medium' },
						],
						default: 'low',
						description: 'Risk classification of the decision',
					},
					{
						displayName: 'Tags',
						name: 'tags',
						type: 'string',
						default: '',
						placeholder: 'finance, loan, high-value',
						description: 'Comma-separated tags to categorise this receipt',
					},
				],
			},

			// ─── Verify / Get Decision Receipt ──────────────────────────────
			{
				displayName: 'Receipt ID',
				name: 'receiptId',
				type: 'string',
				required: true,
				default: '',
				placeholder: 'e.g. STR-1A2B3C4D5E',
				description: 'The unique Signatrust receipt ID to verify or fetch',
				displayOptions: { show: { operation: ['verifyReceipt', 'getReceipt'] } },
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		// The API key itself is injected by the credential's `authenticate`
		// block when using httpRequestWithAuthentication, so we only need
		// baseUrl here to construct request URLs.
		const credentials = await this.getCredentials('signatrustApi');
		const baseUrl = String(credentials.baseUrl).replace(/\/$/, '');

		for (let i = 0; i < items.length; i++) {
			const operation = this.getNodeParameter('operation', i) as string;

			try {
				let responseData: IDataObject;

				if (operation === 'generateReceipt') {
					const agentName = this.getNodeParameter('agentName', i) as string;
					const workflowName = this.getNodeParameter('workflowName', i) as string;
					const action = this.getNodeParameter('action', i) as string;
					const decision = this.getNodeParameter('decision', i) as string;
					const additional = this.getNodeParameter('additionalFields', i, {}) as {
						modelUsed?: string;
						modelProvider?: string;
						modelVersion?: string;
						inputPrompt?: string;
						decisionType?: string;
						riskLevel?: string;
						humanReview?: boolean;
						policies?: string;
						permissions?: string;
						tags?: string;
						includeDecisionInMetadata?: boolean;
					};

					const body: Record<string, unknown> = {
						agent_name: agentName,
						workflow_name: workflowName,
						action,
						decision,
					};

					// Auto-attach n8n execution context so the receipt metadata
					// records exactly where it was generated.
					const workflowId = this.getWorkflow().id;
					if (workflowId) body.workflow_id = workflowId;
					const executionId = this.getExecutionId();
					if (executionId) body.execution_id = executionId;
					body.node_name = this.getNode().name;

					if (additional.modelUsed || additional.modelProvider || additional.modelVersion) {
						body.model = {
							provider: additional.modelProvider || undefined,
							name: additional.modelUsed || undefined,
							version: additional.modelVersion || undefined,
						};
					}
					if (additional.inputPrompt) body.input_prompt = additional.inputPrompt;
					if (additional.decisionType) body.decision_type = additional.decisionType;
					if (additional.riskLevel) body.risk_level = additional.riskLevel;
					if (typeof additional.humanReview === 'boolean')
						body.human_review = additional.humanReview;
					if (additional.policies) body.policies = additional.policies;
					if (additional.permissions) body.permissions = additional.permissions;
					if (additional.tags) body.tags = additional.tags;
					if (additional.includeDecisionInMetadata) {
						body.include_decision_in_metadata = true;
					}

					const opts: IHttpRequestOptions = {
						method: 'POST',
						url: `${baseUrl}/receipts`,
						body,
						json: true,
					};
					responseData = (await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						opts,
					)) as IDataObject;
				} else if (operation === 'verifyReceipt') {
					const receiptId = this.getNodeParameter('receiptId', i) as string;
					const opts: IHttpRequestOptions = {
						method: 'GET',
						url: `${baseUrl}/receipts/${encodeURIComponent(receiptId)}/verify`,
						json: true,
					};
					responseData = (await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						opts,
					)) as IDataObject;
				} else if (operation === 'getReceipt') {
					const receiptId = this.getNodeParameter('receiptId', i) as string;
					const opts: IHttpRequestOptions = {
						method: 'GET',
						url: `${baseUrl}/receipts/${encodeURIComponent(receiptId)}`,
						json: true,
					};
					responseData = (await this.helpers.httpRequestWithAuthentication.call(
						this,
						'signatrustApi',
						opts,
					)) as IDataObject;
				} else {
					throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`, {
						itemIndex: i,
					});
				}

				returnData.push({
					json: responseData,
					pairedItem: { item: i },
				});
			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: { error: (error as Error).message },
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
