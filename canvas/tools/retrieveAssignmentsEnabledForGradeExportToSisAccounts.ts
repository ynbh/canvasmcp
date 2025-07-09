
import { tool } from "ai";
import { retrieveAssignmentsEnabledForGradeExportToSisAccountsDataSchema } from "./aitm.schema.ts";
import { retrieveAssignmentsEnabledForGradeExportToSisAccounts, RetrieveAssignmentsEnabledForGradeExportToSisAccountsData } from "..";

export default tool({
  description: `
  Retrieve assignments enabled for grade export to SIS
Retrieve a list of published assignments
flagged as "post_to_sis".
See the Assignments API for more details on assignments.
Assignment group
and section information are included for convenience.

Each section includes course information for
the origin course and the
cross-listed course, if applicable. The `origin_course` is the course
to
which the section belongs or the course from which the section was
cross-listed. Generally, the
`origin_course` should be preferred when
performing integration work. The `xlist_course` is provided
for consistency
and is only present when the section has been cross-listed.
See Sections API and
Courses Api for me details.

The `override` is only provided if the Differentiated Assignments
course
feature is turned on and the assignment has an override for that section.
When there is an
override for the assignment the override object's
keys/values can be merged with the top level
assignment object to create a
view of the assignment object specific to that section.
See
Assignments api for more information on assignment overrides.

restricts to courses that start
before this date (if they have a start date)
restricts to courses that end after this date (if they
have an end date)
information to include.

"student_overrides":: returns individual student override
information
    `,
  parameters: retrieveAssignmentsEnabledForGradeExportToSisAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RetrieveAssignmentsEnabledForGradeExportToSisAccountsData, "url"> ) => {
    try {
      const { data } = await retrieveAssignmentsEnabledForGradeExportToSisAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    