/**
 *  Mining Attribute-Based Access Control Policies
 * Copyright (C) 2014 Zhongyuan Xu
 * Copyright (C) 2014 Scott D. Stoller
 * Copyright (c) 2014 Stony Brook University
 * Copyright (c) 2014 Research Foundation of SUNY
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see http://www.gnu.org/licenses/.
 */

package edu.dar.util;

import java.util.HashSet;
import java.util.Random;

public class RandomUtil {
	public static <T> T randomElement(HashSet<T> S) {
		if (S == null) {
			return null;
		}
		int size = S.size();
		int item = new Random(System.currentTimeMillis()).nextInt(size);
		int i = 0;
		T result = null;
		for (T obj : S) {
			if (i == item) {
				result = obj;
				break;
			}
			i = i + 1;
		}
		return result;
	}
}
