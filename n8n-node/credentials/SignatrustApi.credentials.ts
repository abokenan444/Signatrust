import {
	IAuthenticateGeneric,
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

export class SignatrustApi implements ICredentialType {
	name = 'signatrustApi';
	displayName = 'Signatrust API';
	documentationUrl = 'https://signatrust.net/docs/api';
	icon = 'file:signatrust.svg' as const;

	authenticate: IAuthenticateGeneric = {
		type: 'generic',
		properties: {
			headers: {
				'X-API-Key': '={{$credentials.apiKey}}',
			},
		},
	};

	properties: INodeProperties[] = [
		{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			typeOptions: {
				password: true,
			},
			default: '',
			required: true,
			description: 'Your Signatrust API key. You can find it in your <a href="https://signatrust.net/dashboard" target="_blank">Signatrust dashboard</a> under Settings → API Keys.',
		},
		{
			displayName: 'Base URL',
			name: 'baseUrl',
			type: 'string',
			default: 'https://api.signatrust.net/v1',
			required: true,
			description: 'The base URL of the Signatrust API. Use the default for <a href="https://signatrust.net" target="_blank">Signatrust Cloud</a>, or enter your self-hosted Enterprise endpoint (e.g. https://signatrust.yourcompany.com/v1).',
		},
	];
}
