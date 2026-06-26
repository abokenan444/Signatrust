import {
	IAuthenticateGeneric,
	ICredentialTestRequest,
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

export class SignatrustApi implements ICredentialType {
	name = 'signatrustApi';

	displayName = 'Signatrust API';

	documentationUrl = 'https://signatrust.net/n8n';

	icon = { light: 'file:signatrust.svg', dark: 'file:signatrust.dark.svg' } as const;

	properties: INodeProperties[] = [
		{
			displayName: 'Connection Type',
			name: 'connectionType',
			type: 'options',
			options: [
				{ name: 'Signatrust Cloud', value: 'cloud' },
				{ name: 'Self-Hosted Enterprise', value: 'selfHosted' },
			],
			default: 'cloud',
			description:
				'Choose Signatrust Cloud (default, https://signatrust.net) or point the node at your self-hosted enterprise endpoint',
		},
		{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			typeOptions: {
				password: true,
			},
			default: '',
			required: true,
			description:
				'Your Signatrust agent API key (starts with sk_live_…). Get one from https://signatrust.net/register; the key is shown once when the agent is created.',
		},
		{
			displayName: 'Base URL',
			name: 'baseUrl',
			type: 'string',
			default: 'https://signatrust.net/api/v1/n8n',
			required: true,
			placeholder: 'e.g. https://signatrust.your-company.com/api/v1/n8n',
			description:
				'Signatrust API base URL. Default is Cloud. For self-hosted enterprise use e.g. https://signatrust.your-company.com/api/v1/n8n.',
			displayOptions: {
				show: { connectionType: ['selfHosted'] },
			},
		},
		{
			displayName: 'Base URL',
			name: 'baseUrl',
			type: 'hidden',
			default: 'https://signatrust.net/api/v1/n8n',
			displayOptions: {
				show: { connectionType: ['cloud'] },
			},
		},
	];

	authenticate: IAuthenticateGeneric = {
		type: 'generic',
		properties: {
			headers: {
				'X-API-Key': '={{$credentials.apiKey}}',
			},
		},
	};

	// Hits the auth-protected /ping endpoint. A green check in the n8n UI
	// means the API key resolved to a live, non-suspended agent.
	test: ICredentialTestRequest = {
		request: {
			baseURL: '={{$credentials.baseUrl}}',
			url: '/ping',
			method: 'GET',
		},
	};
}
