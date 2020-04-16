/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#include <prjxray/database.h>

#include <glob.h>

#include <memory>

#include <absl/strings/str_cat.h>

namespace prjxray {

static constexpr const char kSegbitsGlobPattern[] = "segbits_*.db";

std::vector<std::unique_ptr<prjxray::SegbitsFileReader>> Database::segbits()
    const {
	std::vector<std::unique_ptr<prjxray::SegbitsFileReader>> segbits;

	glob_t segbits_glob_results;
	int ret = glob(absl::StrCat(db_path_, "/", kSegbitsGlobPattern).c_str(),
	               GLOB_NOSORT | GLOB_TILDE, NULL, &segbits_glob_results);
	if (ret < 0) {
		return {};
	}

	for (size_t idx = 0; idx < segbits_glob_results.gl_pathc; idx++) {
		auto this_segbit = SegbitsFileReader::InitWithFile(
		    segbits_glob_results.gl_pathv[idx]);
		if (this_segbit) {
			segbits.emplace_back(std::move(this_segbit));
		}
	}

	globfree(&segbits_glob_results);

	return segbits;
}

}  // namespace prjxray
