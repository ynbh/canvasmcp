
import { tool } from "ai";
import { getBrandConfigVariablesThatShouldBeUsedForThisDomainDataSchema } from "./aitm.schema.ts";
import { getBrandConfigVariablesThatShouldBeUsedForThisDomain, GetBrandConfigVariablesThatShouldBeUsedForThisDomainData } from "..";

export default tool({
  description: `
  Get the brand config variables that should be used for this domain
Will redirect to a static json
file that has all of the brand
variables used by this account. Even though this is a redirect,
do
not store the redirected url since if the account makes any changes
it will redirect to a new url.
Needs no authentication.
    `,
  parameters: getBrandConfigVariablesThatShouldBeUsedForThisDomainDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetBrandConfigVariablesThatShouldBeUsedForThisDomainData, "url"> ) => {
    try {
      const { data } = await getBrandConfigVariablesThatShouldBeUsedForThisDomain(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    