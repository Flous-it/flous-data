import type { FlousDataDump } from "../../../dist/types";

// eslint-disable-next-line @typescript-eslint/no-require-imports
const raw = require("./flous-data.json") as FlousDataDump;

export const data: FlousDataDump = raw;

export function getBanks() {
  return data.banks;
}

export function getAccounts() {
  return data.accounts;
}

export function getFeatures() {
  return data.features;
}

export function getAccountBySlug(slug: string) {
  return data.accounts.find((a) => a.slug === slug) ?? null;
}

export function getBankBySlug(slug: string) {
  return data.banks.find((b) => b.slug === slug) ?? null;
}

export type { FlousDataDump, Bank, Feature, Account, AccountFeature, FeaturePrice } from "../../../dist/types";
